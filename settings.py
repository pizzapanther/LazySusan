import os

from django.conf import settings

LS_TITLE = getattr(settings, 'LS_TITLE', 'Administration')
LS_STATIC = getattr(settings, 'LS_STATIC', '/admin/static/lazysusan/')
LS_STAFF_EMAILS = getattr(settings, 'LS_STAFF_EMAILS', ())

LS_PER_PAGE = getattr(settings, 'LS_PER_PAGE', 25)

LS_DEV = False
if os.environ.has_key('SERVER_SOFTWARE') and os.environ['SERVER_SOFTWARE'].startswith('Dev'):
  LS_DEV = True
  
ADMIN_CONTEXT = {
  'LS_TITLE': LS_TITLE,
  'LS_STATIC': LS_STATIC,
  'LS_DEV': LS_DEV,
}
