import types
import inspect

from django import forms
from django.forms.widgets import MediaDefiningClass

from collections import OrderedDict

from .settings import LS_FORM_MAP
from .widgets import ListWidget
from .utils import static_path
import LazySusan.fields

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
      field = LS_FORM_MAP[db_property.__class__.__name__]
      if type(field) in types.StringTypes:
        field = getattr(LazySusan.fields, field)
        
    elif field is None:
      field = forms.CharField
      
    kwargs['required'] = db_property._required
    if db_property._repeated:
      kwargs['required'] = False
      kwargs = {'repeat_field': field(**kwargs)}
      kwargs['required'] = db_property._required
      field = LazySusan.fields.RepeatedField
      
    field_dict[f] = field(**kwargs)
    
  return field_dict
  
class BootstrapFormMixin (object):
  def __init__ (self, *args, **kwargs):
    super(BootstrapFormMixin, self).__init__(*args, **kwargs)
    for myField in self.fields:
      self.fields[myField].widget.attrs['class'] = 'form-control'
      
class ModelFormMeta (MediaDefiningClass):
  def __new__ (metaname, classname, baseclasses, attrs):
    new_class = super(ModelFormMeta, metaname).__new__(metaname, classname, baseclasses, attrs)
    
    meta = getattr(new_class, 'Meta', None)
    if meta is None:
      return new_class
      
    meta = getattr(new_class, 'Meta', None)
    choices = getattr(meta, 'choices', {})
    overrides = getattr(meta, 'field_overrides', {})
    
    new_class.base_fields = translate_fields(
      new_class.Meta.model,
      new_class.Meta.fields,
      choices,
      overrides
    )
    
    return new_class
    
class ModelForm (forms.BaseForm):
  __metaclass__ = ModelFormMeta
  
  def __init__ (self, *args, **kwargs):
    self.instance = None
    if 'instance' in kwargs:
      self.instance = kwargs['instance']
      del kwargs['instance']
      
    super(ModelForm, self).__init__(*args, **kwargs)
    
  def save (self, commit=True):
    if self.instance:
      for f in self.Meta.fields:
        setattr(self.instance, f, self.cleaned_data[f])
        
    else:
      kwargs = {}
      for f in self.Meta.fields:
        kwargs[f] = self.cleaned_data[f]
        
      self.instance = self.Meta.model(**kwargs)
      
    if commit:
      self.instance.put()
      
    return self.instance
    
class AdminModelForm (BootstrapFormMixin, ModelForm):
  required_css_class = 'required'
  
def generate_form (m, f, c={}, o={}):
  class F (AdminModelForm):
    class Meta:
      model = m
      fields = f
      choices = c
      field_overrides = o
      
  return F
  