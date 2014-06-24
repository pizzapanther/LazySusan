import re

from django import http
from django.template.response import TemplateResponse

from google.appengine.api import users

from .settings import ADMIN_CONTEXT, LS_STATIC

class AdminResponse (TemplateResponse):
  def __init__(self, admin_site, request, template, context=None, mimetype=None, status=None, content_type=None, current_app=None):
    c = ADMIN_CONTEXT.copy()
    c.update(context)
    c['site'] = admin_site
    c['logout_url'] = users.create_logout_url(request.get_full_path())
    
    super(AdminResponse, self).__init__(request, template, c, mimetype, status, content_type, current_app)
    
def valid_choices (choices):
  return [c[0] for c in choices]
  
def static_path (path):
  return LS_STATIC + path
  
def uncamel (text):
  return re.sub("([a-z])([A-Z])","\g<1> \g<2>", text)
  
def unslugify (text):
  return text.replace('-', ' ').replace('_', ' ').title()
  
def cached_method (target):
  def wrapper(*args, **kwargs):
    obj = args[0]
    name = '_' + target.__name__
    
    if not hasattr(obj, name):
      value = target(*args, **kwargs)
      setattr(obj, name, value)
      
    return getattr(obj, name)
    
  return wrapper
  
def get_name (instance):
  if hasattr(instance, '__unicode__'):
    return instance.__unicode__()
    
  elif hasattr(instance, 'key'):
    return instance.key.urlsafe()
    
  return 'Name not found'
  
def gae_admin_required (request):
  user = users.get_current_user()
  if user:
    if users.is_current_user_admin():
      return True, None
      
    return False, http.HttpResponseForbidden('You do not have access to this area.', content_type="text/plain")
    
  return False, users.create_login_url(request.get_full_path())
  