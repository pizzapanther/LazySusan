from django import http

from google.appengine.api import users

from .utils import get_request, AdminResponse

def staff_required (target):
  def wrapper (*args, **kwargs):
    request = get_request(args)
    
    if request.user.is_authenticated():
      if request.user.is_staff:
        return target(*args, **kwargs)
        
      return AdminResponse(request, 'lazysusan/permission_denied.html', {}, status=403)
      
    return http.HttpResponseRedirect(users.create_login_url(request.get_full_path()))
    
  return wrapper
  