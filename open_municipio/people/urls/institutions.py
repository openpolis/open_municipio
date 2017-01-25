from django.conf.urls.defaults import *

from open_municipio.people.views import (CouncilListView, CityGovernmentView, MayorDetailView,
                                         CommitteeDetailView, InstitutionListView, CommitteeListView,
                                         GroupSearchView, GroupDetailView)

urlpatterns = patterns('',
    url(r'^$', InstitutionListView.as_view(), name='om_institution_list'),
    url(r'^mayor/$', MayorDetailView.as_view(), name='om_institution_mayor'),
    url(r'^city-government/$', CityGovernmentView.as_view(), name='om_institution_citigov'),
    url(r'^committees/$', CommitteeListView.as_view(), name='om_institution_committees'),
    url(r'^committees/(?P<slug>[-\w]+)/$', CommitteeDetailView.as_view(), name='om_institution_committee'),
    url(r'^groups/$', GroupSearchView(template='people/group_search.html'), name='om_group_search'),
    url(r'^groups/(?P<slug>[-\w]+)/$', GroupDetailView.as_view(), name='om_institution_group'),
    url(r'^council/$', CouncilListView.as_view(), name='om_institution_council'),
)
