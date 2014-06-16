import re

class Admin (object):
  def __init__ (self):
    self.form = None
    if hasattr(self.Meta, 'form'):
      self.form = self.Meta.form
      
    self.model = None
    if hasattr(self.Meta, 'model'):
      self.model = self.Meta.model
      
    self.name = None
    if hasattr(self.Meta, 'name'):
      self.name = self.Meta.name
      
    elif self.model:
      self.name = re.sub("([a-z])([A-Z])","\g<1> \g<2>", self.model._get_kind())
      
    else:
      raise Exception('Admin not configured with a name or model.')
      
    self.plural = self.name + 's'
    if hasattr(self.Meta, 'plural'):
      self.plural = self.Meta.plural
      