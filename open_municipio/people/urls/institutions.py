from django.conf.urls.defaults import *
from django.views.generic import ListView, TemplateView

from open_municipio.people.models import Institution
from open_municipio.people.views import CouncilView, CityGovernmentView, CommitteeDetailView

urlpatterns = patterns('',
    url(r'^$', ListView.as_view(
           model=Institution,
           template_name='institution_list.html'
        ), name='om_institution_list'),

    url(r'^committees/(?P<slug>[-\w]+)/$', CommitteeDetailView.as_view(), name='om_institution_committee'),
    url(r'^city-government/$', CityGovernmentView.as_view(), name='om_institution_citigov'),
    url(r'^council/$', CouncilView.as_view(), name='om_institution_council'),

    # url(r'^(?P<slug>[-\w]+)/$', InstitutionDetailView.as_view(
    #        template_name='institution_detail.html'
    #     ), name='om_institution_detail'),

)
