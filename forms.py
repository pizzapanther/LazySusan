import types
import inspect

from django import forms
from django.forms.widgets import Media, MediaDefiningClass
from django.forms.fields import Field, FileField
from django.core.exceptions import ValidationError

from collections import OrderedDict

from .settings import LS_FORM_MAP
from .widgets import ListWidget
from .utils import static_path
import LazySusan.fields

def translate_fields (model, fields, choices, overrides, help_text, structured):
  field_dict = OrderedDict()
  
  for f in fields:
    field = None
    
    if f in structured:
      field_dict[f] = structured[f](prefix=f)
      continue
      
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
      
      if db_property.__class__.__name__ == 'TextProperty' and 'widget' not in kwargs:
        kwargs['widget'] = forms.Textarea
        
    if f in help_text:
      kwargs['help_text'] = help_text[f]
      
    kwargs['required'] = db_property._required
    
    if db_property._default is not None:
      kwargs['initial'] = db_property._default
      
    if hasattr(db_property, '_kind'):
      kwargs['kind'] = db_property._kind
      
    if db_property._repeated:
      kwargs['required'] = False
      kwargs = {'repeat_field': field(**kwargs)}
      kwargs['required'] = db_property._required
      field = LazySusan.fields.RepeatedField
      
    field_dict[f] = field(**kwargs)
    field_dict[f].is_structured = False
    
  return field_dict
  
class BootstrapFormMixin (object):
  def __init__ (self, *args, **kwargs):
    super(BootstrapFormMixin, self).__init__(*args, **kwargs)
    for myField in self.fields:
      if isinstance(self.fields[myField].widget, forms.CheckboxInput):
        self.fields[myField].widget.is_checkbox = True
        
      else:
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
    help_text = getattr(meta, 'help_text', {})
    structured = getattr(meta, 'structured', {})
    
    new_class.base_fields = translate_fields(
      new_class.Meta.model,
      new_class.Meta.fields,
      choices,
      overrides,
      help_text,
      structured,
    )
    
    return new_class
    
class ModelForm (forms.BaseForm):
  __metaclass__ = ModelFormMeta
  
  def __init__ (self, *args, **kwargs):
    self.instance = None
    if 'instance' in kwargs:
      self.instance = kwargs['instance']
      del kwargs['instance']
      
    initial = {}
    if 'initial' in kwargs:
      initial = kwargs['initial']
      
    if self.instance:
      instance_initial = {}
      for f in self.Meta.fields:
        instance_initial[f] = getattr(self.instance, f)
        
      instance_initial.update(initial)
      
      kwargs['initial'] = instance_initial
      
    super(ModelForm, self).__init__(*args, **kwargs)
    
    self.formsets = {}
    for f in self:
      if hasattr(f.field, 'is_structured') and f.field.is_structured:
        initial = None
        if 'initial' in kwargs:
          if f.field.prefix in kwargs['initial']:
            initial = kwargs['initial'][f.field.prefix]
            
        if len(self.data.keys()) > 0:
          self.formsets[f.field.prefix] = f.field.formset(
            self.data, self.files,
            prefix=f.field.prefix,
            initial=initial
          )
          
        else:
          self.formsets[f.field.prefix] = f.field.formset(prefix=f.field.prefix, initial=initial)
          
  def _clean_fields (self):
    for name, field in self.fields.items():
      value = field.widget.value_from_datadict(self.data, self.files, self.add_prefix(name))
      try:
        if hasattr(field, 'is_structured') and field.is_structured:
          value = []
          if self.formsets[name].is_valid():
            for form in self.formsets[name]:
              if not form.cleaned_data['DELETE']:
                value.append(form.save(commit=False))
                
        elif isinstance(field, FileField):
          initial = self.initial.get(name, field.initial)
          value = field.clean(value, initial)
          
        else:
          value = field.clean(value)
          
        self.cleaned_data[name] = value
        
        if hasattr(self, 'clean_%s' % name):
          value = getattr(self, 'clean_%s' % name)()
          self.cleaned_data[name] = value
          
      except ValidationError as e:
        self._errors[name] = self.error_class(e.messages)
        if name in self.cleaned_data:
          del self.cleaned_data[name]
          
  def save (self, commit=True):
    import logging
    if self.instance:
      for f in self.Meta.fields:
        logging.info(f)
        logging.info(self.cleaned_data[f])
        
        setattr(self.instance, f, self.cleaned_data[f])
        
    else:
      kwargs = {}
      for f in self.Meta.fields:
        kwargs[f] = self.cleaned_data[f]
        
      logging.info(kwargs)
      self.instance = self.Meta.model(**kwargs)
      
    if commit:
      self.instance.put()
      
    return self.instance
    
  @property
  def media (self):
    media = Media()
    
    for field in self.fields.values():
      media = media + field.widget.media
      
      if hasattr(field, 'is_structured') and field.is_structured:
        media = media + self.formsets[field.prefix].media
        
    return media
    
class AdminModelForm (BootstrapFormMixin, ModelForm):
  required_css_class = 'required'
  
def generate_form (m, f, c={}, o={}, h={}, s={}):
  class F (AdminModelForm):
    class Meta:
      model = m
      fields = f
      choices = c
      field_overrides = o
      help_text = h
      structured = s
      
  return F
  