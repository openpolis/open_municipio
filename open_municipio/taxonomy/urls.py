from django.conf.urls.defaults import *
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from open_municipio.taxonomy.models import Tag


urlpatterns = patterns('',
    url(r'^list$', 'open_municipio.taxonomy.views.tag_list', name='om_tag_list'),

    url(r'^(?P<slug>[-\w]+)/$', 'open_municipio.taxonomy.views.tag_detail', name='om_tag_detail')
)
