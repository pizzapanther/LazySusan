from django import template

register = template.Library()

@register.filter
def get_values (obj, context):
  admin = context[0]
  fields = context[1]
  
  return admin.object_values(obj, fields)
  
@register.filter
def get_dict_value (d, key):
  return d[key]
  