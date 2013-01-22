import types

from django import template

register = template.Library()

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
  