from django.conf.urls.defaults import *

from open_municipio.people.views import (CouncilListView, CityGovernmentView, MayorDetailView,
                                         CommitteeDetailView, InstitutionListView, CommitteeListView,
                                         GroupListView, GroupDetailView)

from django.views.decorators.cache import cache_page

urlpatterns = patterns('',
    url(r'^$', InstitutionListView.as_view(), name='om_institution_list'),
    url(r'^mayor/$', MayorDetailView.as_view(), name='om_institution_mayor'),
    url(r'^city-government/$', cache_page(60 * 720)(CityGovernmentView.as_view()), name='om_institution_citigov'),
    url(r'^committees/$', CommitteeListView.as_view(), name='om_institution_committees'),
    url(r'^committees/(?P<slug>[-\w]+)/$', CommitteeDetailView.as_view(), name='om_institution_committee'),
    url(r'^groups/$', GroupListView.as_view(), name='om_institution_groups'),
    url(r'^groups/(?P<slug>[-\w]+)/$', GroupDetailView.as_view(), name='om_institution_group'),
    url(r'^council/$', cache_page(60 * 720)(CouncilListView.as_view()), name='om_institution_council'),
)
