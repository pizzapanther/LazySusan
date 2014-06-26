import re
import types

from django import http
from django import forms
from django.forms.formsets import formset_factory
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from google.appengine.ext import ndb

from .utils import AdminResponse, uncamel, unslugify, cached_method, get_name
from .forms import generate_form
from .pagination import pagination
from .auth import staff_required, user_id
from .history.models import log_change, log_add, log_delete

class Admin (object):
  list_display = []
  lookup = False
  lookup_list_display = []
  
  def __init__ (self, app):
    self.app = app
    
    self.model = None
    if hasattr(self.Meta, 'model'):
      self.model = self.Meta.model
      
    self.form = None
    if hasattr(self.Meta, 'form'):
      self.form = self.Meta.form
      
    elif self.model:
      choices = getattr(self.Meta, 'choices', {})
      overrides = getattr(self.Meta, 'field_overrides', {})
      help_text = getattr(self.Meta, 'help_text', {})
      structured = getattr(self.Meta, 'structured', {})
      read_only = getattr(self.Meta, 'read_only', ())
      
      self.form = generate_form(
        self.model,
        self.Meta.fields,
        choices, overrides,
        help_text,
        structured,
        read_only
      )
      
    else:
      raise Exception('Admin not configured with a form or model.')
      
    self.slug = None
    if hasattr(self.Meta, 'slug'):
      self.slug = self.Meta.slug
      
    elif self.model:
      self.slug = re.sub("([a-z])([A-Z])","\g<1>-\g<2>", self.model._get_kind()).lower()
      
    else:
      raise Exception('Admin not configured with a slug or model.')
      
    self.name = None
    if hasattr(self.Meta, 'name'):
      self.name = self.Meta.name
      
    elif self.model:
      self.name = uncamel(self.model._get_kind())
      
    else:
      raise Exception('Admin not configured with a name or model.')
      
    self.plural = self.name + 's'
    if hasattr(self.Meta, 'plural'):
      self.plural = self.Meta.plural
      
  @property
  def urls (self):
    return self.get_urls(), self.slug, self.slug
    
  def get_urls (self):
    from django.conf.urls import patterns, url, include
    
    urlpatterns = patterns('',
      url(r'^$', self.list_view, name='list'),
      url(r'^add/$', self.add_view, name='add'),
      url(r'^(\S+)/$', self.edit_view, name='edit'),
    )
    
    return urlpatterns
    
  def add_urlkey (self):
    return ":".join([self.app.site.name, self.app.slug, self.slug, 'add'])
    
  def edit_urlkey (self):
    return ":".join([self.app.site.name, self.app.slug, self.slug, 'edit'])
    
  def list_urlkey (self):
    return ":".join([self.app.site.name, self.app.slug, self.slug, 'list'])
    
  def queryset (self, request, lookup=False):
    return self.model.query()
    
  def log_info (self, request, form=None):
    return None
    
  @staff_required
  @pagination('results')
  def list_view (self, request):
    qs = self.queryset(request)
    
    c = {
      'title': self.plural,
      'results': qs,
      'field_context': (self, self.list_fields(request)),
      'list_field_names': self.list_field_names(request),
      'admin': self,
    }
    
    return AdminResponse(self.app.site, request, 'lazysusan/list.html', c)
    
  def list_field_names (self, request, lookup=False):
    ret = []
    form = self.get_form(request)
    
    for f in self.list_fields(request, lookup=lookup):
      if f == '__unicode__':
        ret.append(self.name)
        
      else:
        if f in form.base_fields and form.base_fields[f].label:
          ret.append(form.base_fields[f].label)
          
        else:
          if f in self.model._properties and self.model._properties[f]._verbose_name:
            ret.append(self.model._properties[f]._verbose_name)
            
          else:
            ret.append(unslugify(f))
            
    return ret
    
  def list_fields (self, request, lookup=False):
    if lookup:
      if self.lookup_list_display:
        return self.lookup_list_display
        
    else:
      if self.list_display:
        return self.list_display
        
    return ('__unicode__',)
    
  @cached_method
  def choices_map (self):
    ret = {}
    if hasattr(self.Meta, 'choices'):
      for field, clist in self.Meta.choices.items():
        ret[field] = {}
        for choice in clist:
          if type(choice) in (types.TupleType, types.ListType) and len(choice) > 1:
            ret[field][choice[0]] = choice[1]
            
    return ret
    
  def object_values (self, obj, fields):
    ret = []
    for field in fields:
      attr = getattr(obj, field, None)
      if type(attr) == types.MethodType:
        if getattr(attr, 'is_safe', False):
          attr = mark_safe(attr())
          
        else:
          attr = attr()
          
      else:
        cmap = self.choices_map()
        if field in cmap:
          if attr in cmap[field]:
            attr = cmap[field][attr]
            
      ret.append(attr)
      
    return ret
    
  def get_form (self, request):
    return self.form
    
  def form_view (self, request, action, instance=None):
    if request.POST:
      form = self.get_form(request)(request.POST, instance=instance)
      
    else:
      form = self.get_form(request)(instance=instance)
      
    if request.POST:
      if form.is_valid():
        instance = form.save(commit=False)
        self.pre_save(request, instance, form)
        instance.put()
        self.post_save(request, instance, form)
        
        if action == 'Update':
          #todo: make user id more generic
          log_change(instance, form, user=user_id(request), additional_info=self.log_info(request, form))
          
        else:
          log_add(instance, user=user_id(request), additional_info=self.log_info(request, form))
          
        return http.HttpResponseRedirect(reverse(self.list_urlkey()))
        
    c = {
      'title': action + ' ' + self.name,
      'action': action,
      'ngApp': 'lsform',
      'form': form,
      'admin': self,
    }
    
    if action == 'Update':
      c['title'] += ': ' + get_name(instance)
      
    return AdminResponse(self.app.site, request, 'lazysusan/form.html', c)
    
  @staff_required
  def add_view (self, request):
    return self.form_view(request, 'Add')
    
  def pre_save (self, request, instance, form):
    return None
    
  def post_save (self, request, instance, form):
    return None
    
  @staff_required
  def edit_view (self, request, key):
    try:
      key = ndb.Key(urlsafe=key)
      
    except:
      raise http.Http404
      
    if key.kind() != self.model._get_kind():
      raise http.Http404
      
    instance = key.get()
    if instance is None:
      raise http.Http404
      
    return self.form_view(request, 'Update', instance)
    
class StructuredMixin (object):
  def get (self, name, initial):
    data = getattr(self, name, initial)
    if data is None:
      data = initial
      
    return data
    
class StructuredAdmin (Admin):
  is_structured = True
  
  def __init__ (self, prefix):
    self.label = None
    self.help_text = None
    self.widget = forms.TextInput()
    self.required = False
    self.show_hidden_initial = True
    self.localize = False
    self.initial = None
    
    self.prefix = prefix
    
    super(StructuredAdmin, self).__init__(None)
    
    self.formset = formset_factory(self.form, can_delete=True)
    
  def prepare_value (self, data):
    return data
    
  def hidden_widget (self):
    return forms.HiddenInput()
    
  def _has_changed (self, initial, data):
    return False
    
  def to_python (self, value):
    return value
    