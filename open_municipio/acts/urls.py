from django.conf.urls.defaults import *

from open_municipio.acts.models import Act
from open_municipio.acts.views import ActDetailView, ActListView, ActAddTagsView, ActRemoveTagView
from voting.views import vote_on_object

act_dict = {
    'model': Act,
    'template_object_name': 'act',
    'allow_xmlhttprequest': 'true',
}

urlpatterns = patterns('',
    url(r'^$', ActListView.as_view(),  name='om_act_list'),                       
    url(r'^(?P<pk>\d+)/$', ActDetailView.as_view(),  name='om_act_detail'),
    url(r'^(?P<pk>\d+)/(?P<tab>documents\w+)/$', ActDetailView.as_view(),  name='om_act_detail_documents'),
    url(r'^(?P<pk>\d+)/(?P<tab>emendations\w+)/$', ActDetailView.as_view(),  name='om_act_detail_emendations'),
    url(r'^(?P<pk>\d+)/(?P<tab>votes\w+)/$', ActDetailView.as_view(),  name='om_act_detail_votes'),
    url(r'^(?P<pk>\d+)/$', ActDetailView.as_view(),  name='om_act_detail'),
    url(r'^(?P<pk>\d+)/tags/add/$', ActAddTagsView.as_view(),  name='om_act_tags_add'),
    url(r'^(?P<act_pk>\d+)/tags/remove/(?P<tag_slug>[-\w]+)/$', ActRemoveTagView.as_view(),  name='om_act_tags_remove'),
    url(r'^(?P<object_id>\d+)/(?P<direction>up|down|clear)vote/?$', vote_on_object, act_dict),
)
