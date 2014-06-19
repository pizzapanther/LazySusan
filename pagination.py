from django import http

from google.appengine.ext.db import Query

from .settings import LS_PER_PAGE

class Page (object):
  def __init__ (self, objects, start_cursor, next_cursor, more):
    self.objects = objects
    self.start_cursor = start_cursor
    self.next_cursor = next_cursor
    self.more = more
    
  def has_previous (self):
    if self.start_cursor:
      return True
      
    return False
    
  def has_next (self):
    if self.more:
      return True
      
    return False
    
class LSPaginator (object):
  def __init__ (self, request, query, per_page, page_param='page'):
    self.request = request
    self.page_param = page_param
    self.per_page = per_page
    self.query = query
    
  def page (self, cursor=None):
    objects, next_cursor, more = self.query.fetch_page(self.per_page, start_cursor=cursor)
    return Page(objects, cursor, next_cursor, more)
    
  def current (self):
    if not hasattr(self, '_current'):
      page = self.request.REQUEST.get(self.page_param, None)
      self._current = self.page(page)
      
    return self._current
    
  def current_list (self):
    return self.current().objects
    
  def has_previous (self):
    return self.current().has_previous()
    
  def has_next (self):
    return self.current().has_next()
    
  def previous_qs (self):
    qs = self.request.META['QUERY_STRING']
    cs = '%s=%d' % (self.page_param, self.number())
    if self.has_previous():
      ps = '%s=%d' % (self.page_param, self.number() - 1)
      if qs:
        if cs in qs:
          qs = qs.replace(cs, ps)
          
        else:
          qs = qs + '&' + ps
          
      else:
        qs = ps
        
    return qs
    
  def next_qs (self):
    qs = self.request.META['QUERY_STRING']
    cs = '%s=%d' % (self.page_param, self.number())
    if self.has_next():
      ps = '%s=%d' % (self.page_param, self.number() + 1)
      
      if qs:
        if cs in qs:
          qs = qs.replace(cs, ps)
          
        else:
          qs = qs + '&' + ps
          
      else:
        qs = ps
        
    return qs
    
def pagination (query_var, per_page=LS_PER_PAGE, page_param='page', output_var='paginator'):
  def decorator(target):
    def wrapper(*args, **kwargs):
      request = None
      for a in args:
        if isinstance(a, http.HttpRequest):
          request = a
          break
        
      tpl_response = target(*args, **kwargs)
      tpl_response.context_data[output_var] = LSPaginator(
                                                          request,
                                                          tpl_response.context_data[query_var],
                                                          per_page,
                                                          page_param,
                                                         )
      
      return tpl_response
      
    return wrapper
    
  return decorator
  