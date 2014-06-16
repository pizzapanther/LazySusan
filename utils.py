from django.template.response import TemplateResponse

from .settings import ADMIN_CONTEXT

class AdminResponse (TemplateResponse):
  def __init__(self, admin_site, request, template, context=None, mimetype=None, status=None, content_type=None, current_app=None):
    c = ADMIN_CONTEXT.copy()
    c.update(context)
    c['site'] = admin_site
    
    super(AdminResponse, self).__init__(request, template, c, mimetype, status, content_type, current_app)
    