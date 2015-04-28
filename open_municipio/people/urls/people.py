from django.conf.urls.defaults import *
from open_municipio.people.views import PoliticianDetailView, PoliticianListView, \
            PoliticianSearchView, ChargeSearchView

urlpatterns = patterns('',
    url(r'^$', PoliticianListView.as_view(), name='om_politician_list'),

    # faceted navigation
    url(r'^charge/$', ChargeSearchView(template='people/charge_search.html'), name='charge_search'),

    url(r'^search/$', PoliticianSearchView.as_view(), name='om_politician_search'),
    url(r'^(?P<slug>[-\w]+)/$', PoliticianDetailView.as_view(), name='om_politician_detail'),
    url(r'^(?P<slug>[-\w]+)/(?P<institution_slug>[-\w]+)-(?P<year>[0-9]+)-(?P<month>[0-9]+)-(?P<day>[0-9]+)/$', PoliticianDetailView.as_view(), name='om_politician_detail'),
)
