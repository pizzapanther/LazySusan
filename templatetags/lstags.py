import re
import types
import logging

from django import template

register = template.Library()

@register.filter
def add_class (html_obj, cls):
  html = str(html_obj)
  html = re.sub('(<\S+) ', r'\1 class="' + cls + '" ', html)
  return html
  
@register.filter
def narf (thing):
  logging.info(thing)
  logging.info(dir(thing))
  return thing
  
@register.filter
def get_key (instance):
  if hasattr(instance.key, 'urlsafe'):
    return instance.key.urlsafe()
    
  return instance.key()
  
@register.filter
def uname (obj):
  return obj.__unicode__()
  
@register.filter
def list_fields (instance, request):
  return instance.list_fields(request)
  
@register.filter
def list_field_names (instance, request):
  return instance.list_field_names(request)
  
@register.filter
def get_attr (row, field):
  attr = getattr(row, field)
  if type(attr) == types.MethodType:
    return attr()
    
  return attr
  