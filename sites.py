import json
import hashlib

from django import http
from django.template import loader, TemplateDoesNotExist, Context
from django.utils.importlib import import_module

from google.appengine.api import memcache

from .auth import staff_required
from .utils import AdminResponse
from .pagination import pagination

class AdminSite (object):
  def __init__ (self, import_list, name=None, app_name=None, cache_namespace='LazySusanAdmin'):
    self.apps = []
    self.import_list = import_list
    self.name = name or 'admin'
    self.app_name = app_name or 'admin'
    self.lookups = {}
    self.load_apps()
    self.cache_namespace = cache_namespace
    
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
      url(r'^ng-template/(\S+)$', self.ng_template_view, name='ng-template'),
      url(r'^kind-lookup/$', self.kind_lookup_view, name='kind-lookup'),
    )
    
    for app in self.apps:
      urlpatterns += patterns('', url(r'^' + app.slug + '/', include(app.urls)))
      
    return urlpatterns
    
  @staff_required
  def index_view (self, request):
    return AdminResponse(self, request, 'lazysusan/index.html', {})
    
  @staff_required
  def ng_template_view (self, request, path):
    try:
      t = loader.get_template('lazysusan/ng/' + path)
      
    except TemplateDoesNotExist:
      raise http.Http404
      
    return http.HttpResponse(t.render(Context({})))
    
  def add_lookup (self, admin):
    self.lookups[admin.model._get_kind()] = admin
    
  def cache_key (self, request, thing):
    key = '{}-{}-{}'.format(thing, request.path, request.user_id)
    return hashlib.sha224(key).hexdigest()
    
  @staff_required
  @pagination('results')
  def kind_lookup_view (self, request):
    try:
      parameter = json.loads(request.body)
      
    except:
      search = request.GET.get('search', '')
      kind = request.GET.get('kind', '')
      
    else:
      search = parameter.get('search', '')
      kind = parameter.get('kind', '')
      
    data = {'status': 'Invalid'}
    
    if kind in self.lookups:
      param_cache_key = self.cache_key(request, 'params-' + kind)
      if 'use_cache' in parameter and parameter['use_cache']:
        p = memcache.get(param_cache_key, namespace=self.cache_namespace)
        if p:
          parameter = p
          
      else:
        memcache.set(param_cache_key, parameter, namespace=self.cache_namespace)
        
      admin = self.lookups[kind]
      results = []
      query = admin.queryset(request, True)
      query = admin.apply_list_filters(request, query, lookup=True, json=parameter)
      query = admin.apply_search_filters(request, query, parameter['search'])
      
      filters = []
      for f in admin.list_filters:
        for d in f.display_values_json(parameter):
          filters.append(d)
          
      c = {
        'field_context': (admin, admin.list_fields(request, True)),
        'list_field_names': admin.list_field_names(request, True),
        'results': query,
        'admin': admin,
        'kind': kind,
        'applied_filters': filters,
        'search': parameter['search'],
      }
      return AdminResponse(self, request, 'lazysusan/ng/KindResults.json', c, content_type='application/json')
      
    else:
      data['message'] = kind + ' lookups not configured.'
      
    return http.HttpResponse(json.dumps(data), content_type='application/json')
    
  def ng_template_urlkey (self):
    return ":".join([self.name, 'ng-template'])
    
  def kind_lookup_urlkey (self):
    return ":".join([self.name, 'kind-lookup'])
    
  def index_urlkey (self):
    return ":".join([self.name, 'index'])
    