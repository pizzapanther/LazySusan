from django import http
from django.template.response import TemplateResponse

from .settings import ADMIN_CONTEXT

class NoRequest (Exception):
  pass

class ImproperConfiguration (Exception):
  pass

class AdminResponse (TemplateResponse):
  def __init__(self, request, template, context=None, mimetype=None, status=None, content_type=None, current_app=None):
    c = ADMIN_CONTEXT.copy()
    c.update(context)
    super(AdminResponse, self).__init__(request, template, c, mimetype, status, content_type, current_app)
    
def get_request (args):
  request = None
  for a in args:
    if isinstance(a, http.HttpRequest):
      request = a
      break
    
  if request is None:
    raise NoRequest('Request object not passed in as an argument.')
    
  return request
  
def cached_method (target):
  def wrapper(*args, **kwargs):
    obj = args[0]
    name = '_' + target.__name__
    
    if not hasattr(obj, name):
      value = target(*args, **kwargs)
      setattr(obj, name, value)
      
    return getattr(obj, name)
    
  return wrapper
  