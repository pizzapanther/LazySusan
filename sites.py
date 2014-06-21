from django.utils.importlib import import_module

from .auth import staff_required
from .utils import AdminResponse

class AdminSite (object):
  def __init__ (self, import_list, name=None, app_name=None):
    self.apps = []
    self.import_list = import_list
    self.name = name or 'admin'
    self.app_name = app_name or 'admin'
    self.load_apps()
    
  def load_apps (self):
    slugs = []
    
    for app_import in self.import_list:
      if '.AdminApp' in app_import:
        app_import = app_import.replace('.AdminApp', '')
        
      module = import_module(app_import + '.admin')
      app = getattr(module, 'AdminApp')(self)
      if app.slug in slugs:
        raise Exception("Duplicate App Slug")
        
      self.apps.append(app)
      slugs.append(app.slug)
      
  @property
  def urls (self):
    return self.get_urls(), self.app_name, self.name
    
  def get_urls (self):
    from django.conf.urls import patterns, url, include
    
    urlpatterns = patterns('',
      url(r'^$', self.index_view, name='index'),
    )
    
    for app in self.apps:
      urlpatterns += patterns('', url(r'^' + app.slug + '/', include(app.urls)))
      
    return urlpatterns
    
  @staff_required
  def index_view (self, request):
    return AdminResponse(self, request, 'lazysusan/index.html', {})
    