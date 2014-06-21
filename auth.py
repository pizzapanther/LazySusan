import types

from django import http
from django.core.urlresolvers import get_mod_func
from django.utils.importlib import import_module

from .settings import LS_AUTHENTICATOR

def staff_required (target):
  def wrapper (*args, **kwargs):
    if LS_AUTHENTICATOR is None:
      raise Exception('Configure LS_AUTHENTICATOR for staff access to the admin site.')
      
    auther = get_mod_func(LS_AUTHENTICATOR)
    module = import_module(auther[0])
    authenicator = getattr(module, auther[1])
    
    for a in args:
      if isinstance(a, http.HttpRequest):
        request = a
        break
        
    is_staff, response = authenicator(request)
    
    if is_staff:
      return target(*args, **kwargs)
      
    if type(response) in (types.StringType, types.UnicodeType):
      return http.HttpResponseRedirect(response)
      
    return response
    
  return wrapper
  