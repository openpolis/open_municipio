from django.conf.urls.defaults import *
from open_municipio.people.views import SittingCalendarView, SittingDetailView, \
    SittingItemDetailView


urlpatterns = patterns('',
    url(r'^(?P<pk>\d+)/$', SittingDetailView.as_view(), name='om_sitting_detail'),
    url(r'^item/(?P<pk>\d+)/$', SittingItemDetailView.as_view(), name='om_sittingitem_detail'),
    url(r'^calendar/(?P<year>\d{4})/$', SittingCalendarView.as_view(), name='om_sitting_calendar'),

)
    
