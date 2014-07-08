import re
import types
import logging

from google.appengine.ext import ndb

class Search (object):
  def __init__ (self, *fields):
    self.fields = fields
    
  def __call__ (self, instance):
    ret = []
    for field in self.fields:
      loop_instance = instance
      flist = field.split('.')
      break_loop = False
      
      for j, f in enumerate(flist):
        if break_loop:
          break
          
        value = getattr(loop_instance, f)
        
        if isinstance(value, ndb.Key):
          value = value.get()
          if value:
            if j == len(flist) - 1:
              value = unicode(value)
              
          else:
            break_loop = True
            continue
            
        if type(value) == types.MethodType:
          value = value()
          
        loop_instance = value
        
      if value:
        values = re.split('\s+', unicode(value).lower())
        for v in values:
          if v not in ret:
            ret.append(v)
            
    return ret
    
def SearchProperty (*args):
  search = Search(*args)
  return ndb.ComputedProperty(search, repeated=True)
  