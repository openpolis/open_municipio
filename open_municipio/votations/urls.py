from django.conf.urls.defaults import *

from haystack.query import SearchQuerySet

from open_municipio.votations.views import VotationDetailView, VotationSearchView

## SearchQuerySet with multiple facets and highlight
sqs = SearchQuerySet().\
    filter(django_ct='votations.votation').\
    facet('act_type').facet('is_key').\
    facet('organ').\
    query_facet('votation_date', VotationSearchView.DATE_INTERVALS_RANGES['2015']['qrange']).\
    query_facet('votation_date', VotationSearchView.DATE_INTERVALS_RANGES['2014']['qrange']).\
    query_facet('votation_date', VotationSearchView.DATE_INTERVALS_RANGES['2013']['qrange']).\
    order_by('-votation_date').\
    highlight()


urlpatterns = patterns('',
    # faceted navigation
    url(r'^$', VotationSearchView(template='votations/votation_search.html', searchqueryset=sqs), name='om_votation_search'),
    # votation detail
    url(r'^(?P<pk>\d+)/$', VotationDetailView.as_view(), name='om_votation_detail'),
)
