from google.appengine.ext import ndb

from LazySusan.utils import valid_choices

ACTIONS = (
  ('add', 'Added'),
  ('change', 'Changed'),
  ('delete', 'Deleted'),
)

class LogEntry (ndb.Model):
  obj_key = ndb.KeyProperty(verbose_name='Object Key')
  obj_kind = ndb.StringProperty(verbose_name='Kind')
  
  user = ndb.StringProperty()
  
  action = ndb.StringProperty(choices=valid_choices(ACTIONS))
  action_time = ndb.DateTimeProperty(auto_now_add=True)
  
  diff = ndb.TextProperty()
  
  additional_info = ndb.StringProperty()
  
  def Diff (self):
    if self.diff:
      return '<pre>' + self.diff + '</pre>'
      
    return self.diff
    
  Diff.is_safe = True
  
  def ObjectKey (self):
    return self.obj_key.urlsafe()
    
def log_change (instance, form, user=None, additional_info=None):
  if hasattr(form, 'changed_data'):
    diff = 'Updated: '
    diff += ', '.join(form.changed_data)
    diff += '\n'
    
    if hasattr(form, 'formsets'):
      for prefix, formset in form.formsets.items():
        mydiff = ''
        if formset.initial_form_count() == formset.total_form_count():
          title = ' updated:\n'
          
        elif formset.initial_form_count() < formset.total_form_count():
          title = ' added/updated:\n'
          
        else:
          title = ' removed/updated:\n'
          
        for form in formset:
          if form.changed_data:
            if 'DELETE' in form.changed_data:
              mydiff += '  Deleted Item'
              
            else:
              mydiff += '  '
              mydiff += ', '.join(form.changed_data)
              mydiff += '\n'
              
        if mydiff:
          diff += prefix + title + mydiff + "\n"
          
  else:
    diff = form
    
  entry = LogEntry(
    obj_key=instance.key,
    obj_kind=instance._get_kind(),
    user=user,
    action='change',
    diff=diff,
    additional_info=additional_info,
  )
  entry.put()
  
def log_add (instance, user=None, additional_info=None):
  entry = LogEntry(
    obj_key=instance.key,
    obj_kind=instance._get_kind(),
    user=user,
    action='add',
    additional_info=additional_info
  )
  entry.put()
  
def log_delete (instance, additional_info=None):
  entry = LogEntry(
    obj_key=instance.key,
    obj_kind=instance._get_kind(),
    user=user, action='delete',
    additional_info=additional_info
  )
  entry.key.delete()
  