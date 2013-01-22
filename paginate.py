from django.core.paginator import Page, Paginator, EmptyPage, PageNotAnInteger
from django import http

from google.appengine.ext.db import Query

from .settings import LS_PER_PAGE

class LSPaginator (Paginator):
  def __init__ (self, request, object_list, per_page, page_param='page', orphans=0, allow_empty_first_page=True):
    self.request = request
    self.page_param = page_param
    
    super(LSPaginator, self).__init__ (object_list, per_page, orphans=orphans, allow_empty_first_page=allow_empty_first_page)
    
  def page (self, number):
    number = self.validate_number(number)
    bottom = (number - 1) * self.per_page
    top = bottom + self.per_page
    if top + self.orphans >= self.count:
      top = self.count
      
    if isinstance(self.object_list, Query):
      return Page(self.object_list.run(offset=bottom, limit=self.per_page), number, self)
      
    return Page(self.object_list[bottom:top], number, self)
    
  def current (self):
    if not hasattr(self, '_current'):
      page = self.request.REQUEST.get(self.page_param, '1')
      
      try:
        self._current = self.page(page)
        
      except PageNotAnInteger:
        self._current = self.page(1)
        
      except EmptyPage:
        self._current = self.page(self.num_pages)
        
    return self._current
    
  def current_list (self):
    return self.current().object_list
    
  def number (self):
    return self.current().number
    
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
    
def pagination (object_list_var, per_page=LS_PER_PAGE, page_param='page', output_var='paginator', orphans=0, allow_empty_first_page=True):
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
                                                          tpl_response.context_data[object_list_var],
                                                          per_page,
                                                          page_param,
                                                          orphans,
                                                          allow_empty_first_page
                                                         )
      
      return tpl_response
      
    return wrapper
    
  return decorator
  