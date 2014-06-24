import urllib
import logging

from django import http
from django.template.response import TemplateResponse

from google.appengine.ext.db import Query
from google.appengine.datastore.datastore_query import Cursor
from google.appengine.ext import db

from .settings import LS_PER_PAGE

class Page (object):
  def __init__ (self, query, per_page, page):
    self.objects = []
    self.query = query
    self.per_page = per_page
    
    try:
      self.page = int(page)
      
    except:
      self.page = 1
      
    else:
      if self.page < 1:
        self.page = 1
        
    self.offset = (self.page - 1) * self.per_page
    self.objects = self.query.fetch(self.per_page, offset=self.offset, read_policy=db.STRONG_CONSISTENCY)
    self.total = self.query.count()
    self.total_pages = self.total / self.per_page
    
    if self.total % self.per_page > 0:
      self.total_pages += 1
      
  def has_previous (self):
    if self.page > 1:
      return True
      
    return False
    
  def has_next (self):
    if self.page + 1 <= self.total_pages:
      return True
      
    return False
    
class LSPaginator (object):
  def __init__ (self, request, query, per_page, page_param='page'):
    self.request = request
    self.page_param = page_param
    self.per_page = per_page
    self.query = query
    
  def page (self, p):
    return Page(self.query, self.per_page, p)
    
  def current (self):
    if not hasattr(self, '_current'):
      page = self.request.REQUEST.get(self.page_param, None)
      self._current = self.page(page)
      
    return self._current
    
  def current_list (self):
    return self.current().objects
    
  def number (self):
    return self.current().page
    
  def total_pages (self):
    return self.current().total_pages
    
  def total (self):
    return self.current().total
    
  def has_previous (self):
    return self.current().has_previous()
    
  def has_next (self):
    return self.current().has_next()
    
  def generate_query_string (self, qs=''):
    for key, value in self.request.GET.dict().items():
      if key != self.page_param:
        if qs:
          qs += '&'
          
        qs += "{}={}".format(key, urllib.quote(value))
        
    if qs:
      qs = '?' + qs
      
    return qs
    
  def prev_qs (self):
    if self.current().page - 1 == 1:
      qs = ''
      
    else:
      qs = '{}={}'.format(self.page_param, self.current().page - 1)
      
    qs = self.generate_query_string(qs)
    
    return qs
    
  def next_qs (self):
    qs = '{}={}'.format(self.page_param, self.current().page + 1)
    qs = self.generate_query_string(qs)
    
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
      if isinstance(tpl_response, TemplateResponse):
        tpl_response.context_data[output_var] = LSPaginator(
                                                            request,
                                                            tpl_response.context_data[query_var],
                                                            per_page,
                                                            page_param,
                                                           )
        
      return tpl_response
      
    return wrapper
    
  return decorator
  