from django.conf.urls.defaults import *

from open_municipio.people.views import (CouncilDetailView, CityGovernmentView, MayorDetailView, 
                                         CommitteeDetailView, InstitutionListView)

urlpatterns = patterns('',
    url(r'^$', InstitutionListView.as_view(), name='om_institution_list'),
    url(r'^mayor/$', MayorDetailView.as_view(), name='om_institution_mayor'),
    url(r'^city-government/$', CityGovernmentView.as_view(), name='om_institution_citigov'),
    url(r'^committees/(?P<slug>[-\w]+)/$', CommitteeDetailView.as_view(), name='om_institution_committee'),
    url(r'^council/$', CouncilDetailView.as_view(), name='om_institution_council'),
)
