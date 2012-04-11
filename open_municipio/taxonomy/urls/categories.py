from django.conf.urls.defaults import *

from open_municipio.taxonomy.views import CategoryDetailView


urlpatterns = patterns('',
    url(r'^(?P<slug>[-\w]+)/$', CategoryDetailView.as_view(), name='om_category_detail'),
)
 
