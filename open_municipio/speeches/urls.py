from django.conf.urls.defaults import patterns, url

from open_municipio.speeches.views import generate_speech_report_pdf, generate_speech_event_report_pdf, generate_speech_event_report_rtf

urlpatterns = patterns('',
    # faceted navigation
    url(r'^(?P<pk>\d+)/pdf/$', generate_speech_report_pdf, name='om_speech_pdf_url'),
    url(r'^event/(?P<event_pk>\d+)/pdf/$', generate_speech_event_report_pdf, name='om_speech_event_pdf_url'),
    url(r'^event/(?P<event_pk>\d+)/rtf/$', generate_speech_event_report_rtf, name='om_speech_event_rtf_url'),

)
