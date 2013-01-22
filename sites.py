from copy import deepcopy

from django.utils.importlib import import_module
from django import http

from .auth import staff_required
from .utils import AdminResponse

class AdminSite (object):
  def __init__ (self, config, name='ls', app_name='ls'):
    self.config = deepcopy(config)
    self.name = name
    self.app_name = app_name
    self.init_admins()
    
  def init_admins (self):
    for app in self.config:
      app[1]['admin_instances'] = []
      for admin_view in app[1]['admins']:
        app[1]['admin_instances'].append(self.get_admin_views(app, admin_view))
        
  def get_admin_views (self, app, admin_class):
    if 'module' in app[1]:
      module = import_module(app[1]['module'])
      
    else:
      import_list = admin_class.split('.')
      module = import_module('.'.join(import_list[:-1]))
      admin_class = import_list[-1]
      
    cls = getattr(module, admin_class)
    return cls(self, app)
    
  @property
  def urls (self):
    return self.get_urls(), self.app_name, self.name
    
  def get_urls (self):
    from django.conf.urls import patterns, url, include
    
    urlpatterns = patterns('',
      url(r'^$', self.index, name='index'),
      url(r'^([\w-]+)/$', self.app_index, name='app_index'),
    )
    
    for app in self.config:
      for admin_view in app[1]['admin_instances']:
        urlpatterns += patterns('',
          url(r'^%s/%s/' % (app[0], admin_view.slug), include(admin_view.urls))
        )
        
    return urlpatterns
    
  def context (self, d):
    ret = {'LS_CONFIG': self.config}
    ret.update(d)
    return ret
    
  @staff_required
  def app_index (self, request, app_slug):
    app = None
    for i, a in enumerate(self.config):
      if a[0] == app_slug:
        app = self.config[i]
        break
      
    if app is None:
      raise http.Http404
      
    return AdminResponse(request, 'lazysusan/app_index.html', self.context({'app': app}))
    
  @staff_required
  def index (self, request):
    
    return AdminResponse(request, 'lazysusan/index.html', self.context({}))
    