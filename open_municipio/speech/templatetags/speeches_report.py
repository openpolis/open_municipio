from django.template import Library
from django.core.urlresolvers import reverse

register = Library()

def get_pdf_link(context):
    return reverse('om_speech_event_pdf_url', kwargs={ 'event_pk':1 })

def get_rtf_link(context):
    return reverse('om_speech_event_rtf_url', kwargs={ 'event_pk':1 })


register.simple_tag(takes_context=True)(get_pdf_link)
register.simple_tag(takes_context=True)(get_rtf_link)
