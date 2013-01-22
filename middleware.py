from google.appengine.api import users

from .settings import LS_STAFF_EMAILS
from .utils import cached_method

class User (object):
  def __init__ (self):
    self.user = None
    self.user_id = None
    self.email = None
    self.nickname = None
    
  @cached_method
  def is_authenticated (self):
    self.user = users.get_current_user()
    
    if self.user:
      self.email = self.user.email()
      self.user_id = self.user.user_id()
      self.nickname = self.user.nickname()
      return True
      
    return False
    
  @property
  def is_staff (self):
    if self.is_authenticated():
      if self.user.email() in LS_STAFF_EMAILS:
        return True
        
    return False
    
class Auth (object):
  def process_request (self, request):
    request.user = User()
    