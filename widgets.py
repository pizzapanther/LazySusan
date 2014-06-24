import json

from django import forms
from django.utils.safestring import mark_safe

from google.appengine.ext import ndb

from .utils import static_path

class KeyWidget (forms.TextInput):
  class Media:
    js = (static_path('js/key-widget-directive.js'),)
    
  def __init__ (self, *args, **kwargs):
    self.kind = kwargs['kind']
    del kwargs['kind']
    super(KeyWidget, self).__init__(*args, **kwargs)
    
  def render (self, name, value, attrs=None):
    if attrs is None:
      attrs = {'id': 'id_' + name}
      
    value_name = ''
    v = None
    if value:
      v = value.urlsafe()
      obj = value.get()
      if obj:
        value_name = unicode(obj)
        
    html = '<div class="key-widget">'
    html += super(KeyWidget, self).render(name, v, attrs=attrs)
    html += '<key-lookup kind="{}" widget="{}"></key-lookup>'.format(self.kind, attrs['id'])
    html += '<div class="clearfix"></div>'
    html += '<div class="name" id="name_{}">{}</div>'.format(attrs['id'], value_name)
    html += '</div>'
    
    return mark_safe(html)
    
class ListWidget (forms.Widget):
  def __init__ (self, repeat_widget, *args, **kwargs):
    self.repeat_widget = repeat_widget
    super(ListWidget, self).__init__(*args, **kwargs)
    
  def value_from_datadict (self, data, files, name):
    return data.getlist(name, [])
    
  def render (self, name, value, attrs=None):
    wid = attrs['id']
    del attrs['id']
    attrs.update(self.attrs)
    attrs['ng-model'] = 'v.value'
    
    if not value:
      value = []
      
    value = json.dumps(value)
    w = self.repeat_widget.render(name, '', attrs)
    html = u'<script type="text/ng-template" id="{}.tpl">{}</script>'.format(wid, w)
    html += u'<list-widget wid="\'{}\'" values=\'{}\'></list-widget>'.format(wid, value)
    
    return mark_safe(html)
    
  class Media:
    js = (static_path('js/list-widget-directive.js'),)
    
class DateTimeWidget (forms.DateTimeInput):
  def __init__ (self, *args, **kwargs):
    super(DateTimeWidget, self).__init__(*args, **kwargs)
    self.format = '%m/%d/%Y %H:%M'
    
  def render (self, name, value, attrs=None):
    if attrs is None:
      attrs = {'id': 'id_' + name}
      
    html = super(DateTimeWidget, self).render(name, value, attrs=attrs)
    html += """<script type="text/javascript">$(document).ready(function () {{ $('#{id}').datetimepicker({{autoclose: true, format: 'mm/dd/yyyy hh:ii'}}); }});</script>""".format(**attrs)
    
    return mark_safe(html)
    
  class Media:
    css = {
      'all': (static_path('lib/datetimepicker/css/bootstrap-datetimepicker.min.css'),)
    }
    
    js = (static_path('lib/moment.min.js'), static_path('lib/datetimepicker/js/bootstrap-datetimepicker.min.js'))
    