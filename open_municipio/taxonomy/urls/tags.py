from django.conf.urls.defaults import *

from open_municipio.taxonomy.views import TagDetailView


urlpatterns = patterns('',
    url(r'^(?P<slug>[-\w]+)/$', TagDetailView.as_view(), name='om_tag_detail'),
)
 
