from django.conf.urls.defaults import *

<<<<<<< HEAD
from open_municipio.acts.views import ActDetailView, ActListView, add_tags_to_act, ActRemoveTagView
=======
from open_municipio.acts.views import ActDetailView, ActListView, ActAddTagsView, ActRemoveTagView
>>>>>>> 5838c397fd150c98346ff0bf549c654a4d6c9486


urlpatterns = patterns('',
    url(r'^$', ActListView.as_view(),  name='om_act_list'),                       
    url(r'^(?P<pk>\d+)/$', ActDetailView.as_view(),  name='om_act_detail'),
    url(r'^(?P<pk>\d+)/(?P<tab>documents\w+)/$', ActDetailView.as_view(),  name='om_act_detail_documents'),
    url(r'^(?P<pk>\d+)/(?P<tab>emendations\w+)/$', ActDetailView.as_view(),  name='om_act_detail_emendations'),
    url(r'^(?P<pk>\d+)/(?P<tab>votes\w+)/$', ActDetailView.as_view(),  name='om_act_detail_votes'),
    url(r'^(?P<pk>\d+)/$', ActDetailView.as_view(),  name='om_act_detail'),
    url(r'^(?P<pk>\d+)/tags/add/$', ActAddTagsView.as_view(),  name='om_act_tags_add'),
    url(r'^(?P<act_pk>\d+)/tags/remove/(?P<tag_slug>[-\w]+)/$', ActRemoveTagView.as_view(),  name='om_act_tags_remove'),
)