from django import forms

from collections import OrderedDict

def translate_fields (model):
  field_dict = OrderedDict()
  field_dict['content'] = forms.CharField(label='Narf')
  
  return field_dict
  
class ModelFormBase (forms.BaseForm):
  pass
  
class ModelFormMeta (type):
  def __new__ (metaname, classname, baseclasses, attrs):
    import logging
      
    new_class = super(ModelFormMeta, metaname).__new__(metaname, classname, baseclasses, attrs)
    
    if baseclasses == (ModelFormBase,):
      return new_class
      
    logging.info(dir(new_class))
    new_class._meta = getattr(new_class, 'Meta', None)
    new_class.base_fields = translate_fields(new_class._meta.model)
    
    return new_class
    
class ModelForm (ModelFormBase):
  __metaclass__ = ModelFormMeta
  
def generate_form (m):
  class F (ModelForm):
    narf = True
    
    class Meta:
      model = m
      
  return F
  