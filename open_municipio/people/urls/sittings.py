from django.conf.urls.defaults import *
from open_municipio.people.views import SittingCalendarView, SittingDetailView


urlpatterns = patterns('',
    url(r'^(?P<pk>\d+)/$', SittingDetailView.as_view(), name='om_sitting_detail'),
    url(r'^calendar/(?P<year>\d{4})/$', SittingCalendarView.as_view(), name='om_sitting_calendar'),

)
    
