from django.conf.urls.defaults import patterns, url

from haystack.query import SearchQuerySet

from open_municipio.acts.views import (ActSearchView, AgendaDetailView,
                                       DeliberationDetailView, InterpellationDetailView,
                                       InterrogationDetailView, MotionDetailView,
                                       ActTransitionAddView, ActTransitionRemoveView, ActTagEditorView, 
                                       ActLiveEditView, RecordVoteOnActView)

from open_municipio.locations.views import ActTagByLocationView


## SearchQuerySet with multiple facets and highlight
sqs = SearchQuerySet().filter(django_ct='acts.act').\
    facet('act_type').facet('is_key').facet('initiative').\
    facet('organ').\
    facet('facet_categories').\
    query_facet('pub_date', ActSearchView.DATE_INTERVALS_RANGES['2012']['qrange']).\
    query_facet('pub_date', ActSearchView.DATE_INTERVALS_RANGES['2011']['qrange']).\
    query_facet('pub_date', ActSearchView.DATE_INTERVALS_RANGES['2010']['qrange']).\
    query_facet('pub_date', ActSearchView.DATE_INTERVALS_RANGES['2009']['qrange']).\
    query_facet('pub_date', ActSearchView.DATE_INTERVALS_RANGES['2008']['qrange']).\
    order_by('-pub_date').\
    highlight()

urlpatterns = patterns('',
    # faceted navigation
    url(r'^$', ActSearchView(template='acts/act_search.html', searchqueryset=sqs), name='om_act_search'),
    # agendas
    url(r'^agendas/(?P<pk>\d+)/$', AgendaDetailView.as_view(),  name='om_agenda_detail'),
    url(r'^agendas/(?P<pk>\d+)/(?P<tab>documents)/$', AgendaDetailView.as_view(),  name='om_agenda_detail_documents'),
    url(r'^agendas/(?P<pk>\d+)/(?P<tab>emendations)/$', AgendaDetailView.as_view(),  name='om_agenda_detail_emendations'),
    # deliberations
    url(r'^deliberations/(?P<pk>\d+)/$', DeliberationDetailView.as_view(),  name='om_deliberation_detail'),
    url(r'^deliberations/(?P<pk>\d+)/(?P<tab>documents)/$', DeliberationDetailView.as_view(),  name='om_deliberation_detail_documents'),
    url(r'^deliberations/(?P<pk>\d+)/(?P<tab>emendations)/$', DeliberationDetailView.as_view(),  name='om_deliberation_detail_emendations'),
    # interpellations
    url(r'^interpellations/(?P<pk>\d+)/$', InterpellationDetailView.as_view(),  name='om_interpellation_detail'),
    url(r'^interpellations/(?P<pk>\d+)/(?P<tab>documents)/$', InterpellationDetailView.as_view(),  name='om_interpellation_detail_documents'),
    url(r'^interpellations/(?P<pk>\d+)/(?P<tab>emendations)/$', InterpellationDetailView.as_view(),  name='om_interpellation_detail_emendations'),
    # interrogations
    url(r'^interrogations/(?P<pk>\d+)/$', InterrogationDetailView.as_view(),  name='om_interrogation_detail'),
    url(r'^interrogations/(?P<pk>\d+)/(?P<tab>documents)/$', InterrogationDetailView.as_view(),  name='om_interrogation_detail_documents'),
    url(r'^interrogations/(?P<pk>\d+)/(?P<tab>emendations)/$', InterrogationDetailView.as_view(),  name='om_interrogation_detail_emendations'),
    # motions
    url(r'^motions/(?P<pk>\d+)/$', MotionDetailView.as_view(),  name='om_motion_detail'),
    url(r'^motions/(?P<pk>\d+)/(?P<tab>documents)/$', MotionDetailView.as_view(),  name='om_motion_detail_documents'),
    url(r'^motions/(?P<pk>\d+)/(?P<tab>emendations)/$', MotionDetailView.as_view(),  name='om_motion_detail_emendations'),
)

## Tag management
urlpatterns += patterns('',
    url(r'^(?P<pk>\d+)/topics/update/$', ActTagEditorView.as_view(),  name='om_act_topics_update'),
)

## Location management
urlpatterns += patterns('',
    url(r'^(?P<pk>\d+)/locations/add/$', ActTagByLocationView.as_view(),  name='om_act_locations_add'),
)

## Act's fields update
urlpatterns += patterns('',
    url(r'^(?P<pk>\d+)/description/update/$', ActLiveEditView.as_view(), name='om_act_description_update'),
    url(r'^(?P<pk>\d+)/title/update/$', ActLiveEditView.as_view(), name='om_act_title_update'),
)

## Transition management
urlpatterns += patterns('',
    url(r'(?P<pk>\d+)/transition/add/', ActTransitionAddView.as_view(), name='om_act_transition_add'),
    url(r'(?P<pk>\d+)/transition/remove/', ActTransitionRemoveView.as_view(), name='om_act_transition_remove'),
)

## Votes casted by users
urlpatterns += patterns('',
    url(r'^(?P<pk>\d+)/vote/(?P<direction>up|down|clear)/$', RecordVoteOnActView.as_view(), name='om_act_record_user_vote'),
)                        