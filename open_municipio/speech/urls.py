from django.conf.urls.defaults import patterns, url
from haystack.query import SearchQuerySet

from open_municipio.speech.views import SpeechSearchView, SpeechDetailView, generate_speech_report_pdf, generate_speech_event_report_pdf, generate_speech_event_report_rtf

sqs = SearchQuerySet().filter(django_ct='speech.speech').\
        query_facet('date',SpeechSearchView.DATE_INTERVALS_RANGES['2013']['qrange'])

urlpatterns = patterns('',
    # faceted navigation
    url(r'^$', SpeechSearchView(template='speech/speech_search.html', searchqueryset=sqs),name='om_speech_search'),
    url(r'^(?P<pk>\d+)/$', SpeechDetailView.as_view(),name='om_speech_detail'),
    url(r'^(?P<pk>\d+)/pdf/$', generate_speech_report_pdf, name='om_speech_pdf_url'),
    url(r'^event/(?P<event_pk>\d+)/pdf/$', generate_speech_event_report_pdf, name='om_speech_event_pdf_url'),
    url(r'^event/(?P<event_pk>\d+)/rtf/$', generate_speech_event_report_rtf, name='om_speech_event_rtf_url'),

)
