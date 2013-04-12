from django.conf.urls.defaults import *
from open_municipio.events.views import EventsYearView

urlpatterns = patterns('',
    url(r'^year/(?P<year>\d{4})/$', EventsYearView.as_view(), name='om_events_year'),
)
    
