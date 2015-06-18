from django.conf.urls.defaults import *

from open_municipio.votations.views import VotationDetailView, VotationSearchView

urlpatterns = patterns('',
    # faceted navigation
    url(r'^$', VotationSearchView(template='votations/votation_search.html'), name='om_votation_search'),
    # votation detail (old url, pk)

    url(r'^(?P<pk>\d+)/$', VotationDetailView.as_view(), name='om_votation_detail'),
    # votation detail
    url(r'^(?P<slug>[\w\-]+)/$', VotationDetailView.as_view(), name='om_votation_detail'),
)
