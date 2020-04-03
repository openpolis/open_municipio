from django.conf.urls import *

from open_municipio.locations.views import LocationDetailView, LocationListView


urlpatterns = patterns('',
    url(r'^(?P<slug>[-\w]+)/$', LocationDetailView.as_view(), name='om_location_detail'),
    url(r'^$', LocationListView.as_view(), name='om_location_list'),
)
