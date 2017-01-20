from django.conf.urls.defaults import *

from .views import EventDetailView, EventSearchView

urlpatterns = patterns('',
    # faceted navigation
    url(r'^$', EventSearchView(template='events/event_search.html'), name='om_event_search'),

    # event detail
    url(r'^(?P<pk>\d+)/$', EventDetailView.as_view(), name='om_event_detail'),
    url(r'^(?P<pk>\d+)/(?P<tab>acts)/$', EventDetailView.as_view(), name='om_event_detail_acts'),
)
