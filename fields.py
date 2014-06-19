from django import forms

from google.appengine.api import users

from .widgets import ListWidget

class RepeatedField (forms.Field):
  widget = ListWidget
  
  def __init__ (self, *args, **kwargs):
    self.repeat_field = kwargs['repeat_field']
    del kwargs['repeat_field']
    
    widget = self.widget
    if 'widget' in kwargs:
      widget = kwargs['widget']
      del kwargs['widget']
      
    if isinstance(widget, type):
      widget = widget(self.repeat_field.widget)
      
    self.widget = widget
    
    super(RepeatedField, self).__init__(*args, **kwargs)
    
class UserField (forms.EmailField):
  def clean (self, value):
    value = value.strip()
    clean = super(UserField, self).clean(value)
    
    return self.to_python(clean, True)
    
  def to_python (self, value, convert=False):
    if convert:
      if value:
        import logging
        
        logging.info(value)
        logging.info(users.User(value))
        
        return users.User(value)
        
      return None
      
    return super(UserField, self).to_python(value)
    