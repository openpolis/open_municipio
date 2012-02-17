from django.conf.urls.defaults import *

from open_municipio.acts.views import ActDetailView, add_tags_to_act, ActRemoveTagView


urlpatterns = patterns('',
    url(r'^(?P<pk>\d+)/$', ActDetailView.as_view(),  name='om_act_detail'),
    url(r'^(?P<pk>\d+)/tags/add/$', add_tags_to_act,  name='om_act_tags_add'),
    url(r'^(?P<act_pk>\d+)/tags/remove/(?P<tag_slug>[-\w]+)/$', ActRemoveTagView.as_view(),  name='om_act_tags_remove'),
)