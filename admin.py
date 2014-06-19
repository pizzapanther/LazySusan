import re

from django import http
from django.core.urlresolvers import reverse

from .utils import AdminResponse
from .forms import generate_form
from .pagination import pagination

class Admin (object):
  list_display = []
  
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
      self.form = generate_form(self.model, self.Meta.fields, choices, overrides)
      
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
      self.name = re.sub("([a-z])([A-Z])","\g<1> \g<2>", self.model._get_kind())
      
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
    )
    
    return urlpatterns
    
  def add_urlkey (self):
    return ":".join([self.app.site.name, self.app.slug, self.slug, 'add'])
    
  def list_urlkey (self):
    return ":".join([self.app.site.name, self.app.slug, self.slug, 'list'])
    
  def queryset (self, request):
    return self.model.query()
    
  @pagination('results')
  def list_view (self, request):
    qs = self.queryset(request)
    
    c = {
      'title': self.plural,
      'results': qs,
      'list_fields': self.list_fields(request),
      'list_field_names': self.list_field_names(request),
    }
    
    return AdminResponse(self.app.site, request, 'lazysusan/list.html', c)
    
  def list_field_names (self, request):
    ret = []
    mockup = self.get_form(request)()
    
    for f in self.list_fields(request):
      if f == '__unicode__':
        ret.append(self.name)
        
      else:
        if f in mockup:
          ret.append(mockup[f].label.text)
          
        else:
          ret.append(f)
          
    return ret
    
  def list_fields (self, request):
    if self.list_display:
      return self.list_display
      
    return ('__unicode__',)
    
  def get_form (self, request):
    return self.form
    
  def form_view (self, request, action, instance=None):
    if request.POST:
      form = self.get_form(request)(request.POST, instance=instance)
      
    else:
      form = self.get_form(request)(instance=instance)
      
    if request.POST:
      if form.is_valid():
        form.save()
        return http.HttpResponseRedirect(reverse(self.list_urlkey()))
        
    c = {
      'title': action + ' ' + self.name,
      'action': action,
      'ngApp': 'lsform',
      'form': form,
    }
    return AdminResponse(self.app.site, request, 'lazysusan/form.html', c)
    
  def add_view (self, request):
    return self.form_view(request, 'Add')
    