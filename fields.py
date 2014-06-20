from django import forms

from google.appengine.api import users
from google.appengine.ext import ndb

import pytz

from .widgets import ListWidget, DateTimeWidget

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
        return users.User(value)
        
      return None
      
    return super(UserField, self).to_python(value)
    
class DateTimeField (forms.DateTimeField):
  widget = DateTimeWidget
  
  def to_python (self, value):
    dt = super(DateTimeField, self).to_python(value)
    if dt:
      if dt.tzinfo.zone != 'UTC':
        dt = dt.astimezone(pytz.utc)
        
      dt = dt.replace(tzinfo=None)
      
    return dt
    
class KeyField (forms.Field):
  def to_python (self, value):
    if value:
      return ndb.Key(urlsafe=value)
      
    return None
    