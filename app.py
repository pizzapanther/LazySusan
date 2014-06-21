from .utils import AdminResponse
from .auth import staff_required

class AppBase (object):
  name = None
  slug = None
  admins = ()
  
  def __init__ (self, site):
    self.site = site
    self.admins_init = []
    
    for admin in self.admins:
      self.admins_init.append(admin(self))
      
  def index_urlkey (self):
    return ":".join([self.site.name, self.slug, 'index'])
    
  @property
  def urls (self):
    return self.get_urls(), self.slug, self.slug
    
  def get_urls (self):
    from django.conf.urls import patterns, url, include
    
    urlpatterns = patterns('',
      url(r'^$', self.index_view, name='index'),
    )
    
    for admin in self.admins_init:
      urlpatterns += patterns('', url(r'^' + admin.slug + '/', include(admin.urls)))
      
    return urlpatterns
    
  @staff_required
  def index_view (self, request):
    c = {
      'title': self.name,
      'app': self,
    }
    return AdminResponse(self.site, request, 'lazysusan/app_index.html', c)
    