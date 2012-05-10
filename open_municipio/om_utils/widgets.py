from django import forms
from django.utils.safestring import mark_safe



class HorizontalRadioRenderer(forms.RadioSelect.renderer):
    """
    A custom *renderer* for the ``RadioSelect`` widget which outputs radio buttons 
    horizontally instead of vertically (as the default renderer would do).
    """
    def render(self):
        return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))

