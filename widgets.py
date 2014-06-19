import json

from django import forms
from django.utils.safestring import mark_safe

from .utils import static_path

class ListWidget (forms.Widget):
  def __init__ (self, repeat_widget, *args, **kwargs):
    self.repeat_widget = repeat_widget
    super(ListWidget, self).__init__(*args, **kwargs)
    
  def value_from_datadict (self, data, files, name):
    return data.getlist(name, [])
    
  def render (self, name, value, attrs=None):
    wid = attrs['id']
    del attrs['id']
    attrs.update(self.attrs)
    attrs['ng-model'] = 'v.value'
    
    if not value:
      value = []
      
    value = json.dumps(value)
    w = self.repeat_widget.render(name, '', attrs)
    html = u'<script type="text/ng-template" id="{}.tpl">{}</script>'.format(wid, w)
    html += u'<list-widget wid="\'{}\'" values=\'{}\'></list-widget>'.format(wid, value)
    
    return mark_safe(html)
    
  class Media:
    js = (static_path('js/list-widget-directive.js'),)
    