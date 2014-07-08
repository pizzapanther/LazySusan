import json
import urllib
import logging
import traceback

from google.appengine.api import users

from django import http
from django.conf import settings

from .utils import unslugify

class Filter (object):
  filter_type = 'filter'
  function_namespace = None
  
  class Media:
    js = ()
    css = {}
    
  def render_js (self):
    ret = ''
    for path in self.js_paths():
      ret += '<script type="text/javascript" src="{}"></script>'.format(path)
      
    return ret
    
  def absolute_path (self, path):
    if path.startswith(('http://', 'https://', '/')):
      return path
      
    return settings.STATIC_URL + path
    
  def js_paths (self):
    ret = []
    if hasattr(self.Media, 'js'):
      for path in self.Media.js:
        ret.append(self.absolute_path(path))
        
    return ret
    
  def __init__ (self, attribute, name=None, query_attribute=None, place_holder=''):
    self.attribute = attribute
    self.name = name
    
    self.query_attribute = query_attribute
    self.place_holder = place_holder
    
    if self.name is None:
      self.name = unslugify(self.attribute)
      
  def js_properties (self):
    ret = {}
    for p in self.js_property_list():
      ret[p] = getattr(self, p)
      
    return json.dumps(ret)
    
  def js_properties_template (self):
    return self.js_properties(template=True)
    
  def js_property_list (self):
    return ['name', 'attribute', 'filter_type', 'template', 'function_namespace']
    
  @property
  def template (self):
    return """
      <div class="form-group">
        <input class="form-control" name="filter-{attribute}" id="filter-{attribute}" ng-model="form.value" placeholder="{placeholder}"/>
      </div>
    """.format(name=self.name, attribute=self.attribute, placeholder=self.place_holder)
    
  def get_values (self, request=None, json=None):
    if json:
      ret = []
      for f in json['filters']:
        if f['param'] == self.attribute:
          ret.append(f['value'])
          
      return ret
      
    return request.GET.getlist(self.attribute)
    
  def query_args (self, model, request, json=None):
    args = []
    values = self.get_values(request, json)
    
    for value in values:
      value = self.to_python(value)
      try:
        expressions = self.query_expression(model, value)
        
      except:
        logging.error(traceback.format_exc())
        raise http.Http404
        
      else:
        for e in expressions:
          args.append(e)
          
    return args
    
  def query_expression (self, model, value):
    attr = self.getattr(model)
    
    return [attr == value]
    
  def getattr (self, model):
    if self.query_attribute:
      return self.query_attribute
      
    return getattr(model, self.attribute)
    
  def to_python (self, value):
    return value
    
  def display_values_json (self, jdata):
    ret = []
    values = self.get_values(json=jdata)
    for i, v in enumerate(values):
      f = {"display": self.display(v), "param": self.attribute, "value": v}
      ret.append(json.dumps(f))
      
    return ret
    
  def display_values (self, request):
    ret = []
    values = self.get_values(request)
    
    for i, v in enumerate(values):
      url = self.url_without(request, i)
      ret.append({'url': url, 'display': self.display(v)})
      
    return ret
    
  def display (self, value):
    return self.name + ' is ' + value
    
  def url_without (self, request, skip):
    qs = ''
    
    for key, items in request.GET.iterlists():
      for i, v in enumerate(items):
        if i == skip and key == self.attribute:
          pass
          
        else:
          if qs:
            qs += '&'
            
          qs += key + '=' + urllib.quote(v)
          
    if qs == '':
      qs = 'clear_filters=1'
      
    return request.path + '?' + qs
    
class ChoiceFilter (Filter):
  filter_type = 'choice'
  
  def __init__ (self, attribute, choices, **kwargs):
    self.choices_list = choices
    self.choices = []
    for c in self.choices_list:
      self.choices.append({'name': c[1], 'value': c[0]})
      
    super(ChoiceFilter, self).__init__(attribute, **kwargs)
    
  def js_property_list (self):
    ret = super(ChoiceFilter, self).js_property_list()
    ret.append('choices')
    return ret
    
  def display (self, value):
    for choice in self.choices_list:
      if choice[0] == value:
        value = choice[1]
        break
        
    return self.name + ' is ' + value
    
  @property
  def template (self):
    return """
      <div class="form-group">
        <select class="form-control" name="filter-{attribute}" id="filter-{attribute}" ng-model="form.value" ng-options="choice.value as choice.name for choice in form.which.choices">
          <option value="">--- {name} Choices ---</option>
        </select>
      </div>
    """.format(name=self.name, attribute=self.attribute)
    
class UserFilter (Filter):
  filter_type = 'user'
  
  def to_python (self, value):
    return users.User(value)
    