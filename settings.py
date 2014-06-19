import os

from django.conf import settings
from django import forms

LS_TITLE = getattr(settings, 'LS_TITLE', 'Administration')
LS_STATIC = getattr(settings, 'LS_STATIC', '/admin/static/')
LS_STAFF_EMAILS = getattr(settings, 'LS_STAFF_EMAILS', ())

LS_PER_PAGE = getattr(settings, 'LS_PER_PAGE', 50)

LS_FORM_MAP_DEFAULT = {
  'StringProperty': forms.CharField,
  'IntegerProperty': forms.IntegerField,
  'UserProperty': 'UserField',
}

LS_FORM_MAP = getattr(settings, 'LS_FORM_MAP', LS_FORM_MAP_DEFAULT)

LS_DEV = False
if os.environ.has_key('SERVER_SOFTWARE') and os.environ['SERVER_SOFTWARE'].startswith('Dev'):
  LS_DEV = True
  
ADMIN_CONTEXT = {
  'LS_TITLE': LS_TITLE,
  'LS_STATIC': LS_STATIC,
  'LS_DEV': LS_DEV,
}
