import types

from django.conf.urls import patterns, url, include
from django.template.defaultfilters import slugify
from django import http

from google.appengine.ext.db import Key

from ..utils import ImproperConfiguration, AdminResponse
from ..paginate import pagination
from LazySusan import djangoforms

class AdminViews (object):
  slug = None
  name = None
  name_plural = None
  model = None
  form = None
  list_display = None
  list_search = None
  
  def __init__ (self, site, app):
    self.site = site
    self.app = app
    
    if self.model is None:
      raise ImproperConfiguration('No model attribute configured for Admin View')
      
    if self.slug is None:
      self.slug = slugify(self.model.__name__)
      
    if self.name is None:
      self.name = self.slug[0].upper() + self.slug[1:]
      
    if self.name_plural is None:
      self.name_plural = self.name + 's'
      
    if self.form is None:
      class F (djangoforms.ModelForm):
        class Meta:
          model = self.model
          
      self.form = F
      
  @property
  def urls (self):
    urlpatterns = patterns('',
      url(r'^$', self.list_view, name='list'),
      url(r'^add/$', self.add_view, name='add'),
      url(r'^(\S+)/$', self.change_view, name='change'),
    )
    
    return urlpatterns, self.slug, self.name
    
  def response (self, request, tpl, context):
    c = {'view': self}
    c.update(context)
    return AdminResponse(request, tpl, c)
    
  @pagination('results')
  def list_view (self, request):
    qs = self.queryset(request)
    search = request.GET.get('search', '')
    qs = self.filter_queryset(qs, request, search)
    return self.response(request, 'lazysusan/list_view.html', {'results': qs, 'search': search})
    
  def filter_queryset (self, qs, request, search):
    if search and self.list_search:
      qs.filter('%s =' % self.list_search, search)
      
    return qs
    
  def add_view (self, request):
    pass
  
  def change_view (self, request, key):
    obj = self.get_object(request, key)
    form_class = self.get_form(request)
    f = form_class(request.POST or None, instance=obj)
    if request.method == 'POST':
      if f.is_valid():
        f.save()
        return http.HttpResponseRedirect('../')
        
    c = {
      'form': f,
      'obj': obj,
      'action': 'change',
    }
    return self.response(request, 'lazysusan/form_view.html', c)
  
  def list_field_names (self, request):
    ret = []
    mockup = self.get_form(request)()
    
    for f in self.list_fields(request):
      if f == '__unicode__':
        ret.append(self.name)
        
      else:
        if f in mockup.fields:
          ret.append(mockup[f].label)
          
        else:
          ret.append(f)
          
    return ret
    
  def list_fields (self, request):
    if self.list_display:
      return self.list_display
      
    return ('__unicode__',)
    
  def queryset (self, request):
    return self.model.all()
    
  def get_form (self, request):
    return self.form
    
  def get_object (self, request, key):
    qs = self.queryset(request)
    obj = qs.filter('__key__ =', Key(key)).get()
    if obj is None:
      raise http.Http404
      
    return obj
    
