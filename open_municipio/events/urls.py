from django.conf.urls.defaults import *
from open_municipio.events.views import EventDetailView,EventsYearView, EventActSpeechesView

urlpatterns = patterns('',
    url(r'^(?P<pk>\d+)/$', EventDetailView.as_view(), name='om_event_detail'),
    url(r'^(?P<pk>\d+)/speeches/(?P<act_pk>\w+)/$', EventActSpeechesView.as_view(), name='om_event_speeches_list'),
    url(r'^year/(?P<year>\d{4})/$', EventsYearView.as_view(), name='om_events_year'),
)
    
