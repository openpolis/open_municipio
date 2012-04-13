from django.conf.urls.defaults import *

from open_municipio.locations.views import LocationDetailView


urlpatterns = patterns('',
    url(r'^(?P<slug>[-\w]+)/$', LocationDetailView.as_view(), name='om_location_detail'),
)