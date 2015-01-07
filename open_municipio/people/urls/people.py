from django.conf.urls.defaults import *
from open_municipio.people.views import PoliticianDetailView, PoliticianListView, PoliticianSearchView

from django.views.decorators.cache import cache_page

urlpatterns = patterns('',
    url(r'^$', cache_page(60 * 720)(PoliticianListView.as_view()), name='om_politician_list'),
    url(r'^search/$', PoliticianSearchView.as_view(), name='om_politician_search'),
    url(r'^(?P<slug>[-\w]+)/$', cache_page(60 * 720)(PoliticianDetailView.as_view()), name='om_politician_detail'),
)
