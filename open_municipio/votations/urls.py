from django.conf.urls.defaults import *
from django.views.generic import ListView, TemplateView
from open_municipio.votations.models import Votation
from open_municipio.votations.views import VotationDetailView


urlpatterns = patterns('',
    url(r'^$', ListView.as_view(model=Votation,), name='om_votation_list'),
    url(r'^(?P<pk>\d+)/$', VotationDetailView.as_view(), name='om_votation_detail'),
)
