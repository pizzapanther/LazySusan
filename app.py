from .utils import AdminResponse

class AppBase (object):
  name = None
  slug = None
  admins = ()
  
  def __init__ (self, site):
    self.site = site
    
  def app_index_namspace (self):
    return ":".join([self.site.name, self.slug, 'index'])
    
  @property
  def urls (self):
    return self.get_urls(), self.slug, self.slug
    
  def get_urls (self):
    from django.conf.urls import patterns, url, include
    
    urlpatterns = patterns('',
      url(r'^$', self.index, name='index'),
    )
    
    return urlpatterns
    
  def index (self, request):
    c = {
      'title': self.name,
      'app': self,
    }
    return AdminResponse(self.site, request, 'lazysusan/app_index.html', c)
    