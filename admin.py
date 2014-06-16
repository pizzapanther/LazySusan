import re

from .utils import AdminResponse
from .forms import generate_form

class Admin (object):
  def __init__ (self, app):
    self.app = app
    
    self.model = None
    if hasattr(self.Meta, 'model'):
      self.model = self.Meta.model
      
    self.form = None
    if hasattr(self.Meta, 'form'):
      self.form = self.Meta.form
      
    elif self.model:
      self.form = generate_form(self.model)
      
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
    
  def list_view (self, request):
    pass
    
  def add_view (self, request):
    if request.POST:
      form = self.form(request.POST)
      
    else:
      form = self.form()
      
    c = {
      'title': 'Add ' + self.name,
      'form': form,
    }
    return AdminResponse(self.site, request, 'lazysusan/list.html', c)
    