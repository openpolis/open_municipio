from django.conf.urls.defaults import *
from django.views.generic import TemplateView

from haystack.query import SearchQuerySet
from open_municipio.votations.views import VotationSearchView


## SearchQuerySet with multiple facets and highlight
sqs = SearchQuerySet().filter(django_ct='votations.votation').\
    facet('act_type').facet('is_key').\
    facet('organ').\
    query_facet('votation_date', VotationSearchView.THREEDAYS).\
    query_facet('votation_date', VotationSearchView.ONEMONTH).\
    query_facet('votation_date', VotationSearchView.ONEYEAR).\
    highlight()

urlpatterns = patterns('',
    # faceted navigation
    url(r'^$', VotationSearchView(template='votations/votation_search.html', searchqueryset=sqs), name='om_votation_search'),
    # votation detail
    url(r'^(\d+)/$', TemplateView.as_view(template_name="votations/votation_detail.html"),  name='om_votation_detail'),
)
