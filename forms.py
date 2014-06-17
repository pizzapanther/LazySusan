import inspect

from django import forms

from collections import OrderedDict

from .settings import LS_FORM_MAP

class RepeatedField (forms.Field):
  def __init__ (self, repeat_field, *args, **kwargs):
    self.repeat_field = repeat_field
    super(RepeatedField, self).__init__(*args, **kwargs)
    
def translate_fields (model, fields, choices, overrides):
  field_dict = OrderedDict()
  
  for f in fields:
    field = None
    
    if f in overrides:
      if inspect.isclass(overrides[f]):
        field = overrides[f]
        
      else:
        field_dict[f] = overrides[f]
        continue
        
    db_property = model._properties[f]
    kwargs = {'required': False}
    if db_property._choices:
      if field is None:
        field = forms.ChoiceField
        
      kwargs['choices'] = choices[f]
      
    elif db_property.__class__.__name__ in LS_FORM_MAP:
      field = getattr(forms, LS_FORM_MAP[db_property.__class__.__name__])
      
    elif field is None:
      field = forms.CharField
      
    kwargs['required'] = db_property._required
    if db_property._repeated:
      kwargs['required'] = False
      kwargs = {'repeat_field': field(**kwargs)}
      kwargs['required'] = db_property._required
      field = RepeatedField
      
    field_dict[f] = field(**kwargs)
    
  return field_dict
  
class BootstrapFormMixin (object):
  def __init__ (self, *args, **kwargs):
    super(BootstrapFormMixin, self).__init__(*args, **kwargs)
    for myField in self.fields:
      self.fields[myField].widget.attrs['class'] = 'form-control'
      
class ModelFormBase (BootstrapFormMixin, forms.BaseForm):
  required_css_class = 'required'
  
class ModelFormMeta (type):
  def __new__ (metaname, classname, baseclasses, attrs):
    new_class = super(ModelFormMeta, metaname).__new__(metaname, classname, baseclasses, attrs)
    
    if baseclasses == (ModelFormBase,):
      return new_class
      
    choices = getattr(new_class.Meta, 'choices', {})
    overrides = getattr(new_class.Meta, 'field_overrides', {})
    
    new_class.base_fields = translate_fields(
      new_class.Meta.model,
      new_class.Meta.fields,
      choices,
      overrides
    )
    
    return new_class
    
class ModelForm (ModelFormBase):
  __metaclass__ = ModelFormMeta
  
def generate_form (m, f, c={}, o={}):
  class F (ModelForm):
    class Meta:
      model = m
      fields = f
      choices = c
      field_overrides = o
      
  return F
  