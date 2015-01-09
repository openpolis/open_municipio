from django.conf.urls.defaults import *
from open_municipio.people.views import PoliticianDetailView, PoliticianListView, PoliticianSearchView

urlpatterns = patterns('',
    url(r'^$', PoliticianListView.as_view(), name='om_politician_list'),
    url(r'^search/$', PoliticianSearchView.as_view(), name='om_politician_search'),
    url(r'^(?P<slug>[-\w]+)/$', PoliticianDetailView.as_view(), name='om_politician_detail'),
)
