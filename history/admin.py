import LazySusan

from .models import LogEntry

class LogEntryAdmin (LazySusan.Admin):
  list_display = ('ObjectKey', 'obj_kind', 'user', 'action', 'action_time', 'Diff', 'additional_info')
  
  class Meta:
    model = LogEntry
    fields = ()
    plural = 'Log Entries'
    
class AdminApp (LazySusan.AppBase):
  name = 'History'
  slug = 'history'
  admins = (LogEntryAdmin,)
  