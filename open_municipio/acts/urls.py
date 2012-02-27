from django.conf.urls.defaults import *

from open_municipio.acts.models import Act
from open_municipio.acts.views import ActDetailView, add_tags_to_act, ActRemoveTagView
from voting.views import vote_on_object

act_dict = {
    'model': Act,
    'template_object_name': 'act',
    'allow_xmlhttprequest': 'true',
}


urlpatterns = patterns('',
    url(r'^(?P<pk>\d+)/$', ActDetailView.as_view(), name='om_act_detail'),
    url(r'^(?P<pk>\d+)/tags/add/$', add_tags_to_act, name='om_act_tags_add'),
    url(r'^(?P<act_pk>\d+)/tags/remove/(?P<tag_slug>[-\w]+)/$', ActRemoveTagView.as_view(), name='om_act_tags_remove'),
    url(r'^(?P<object_id>\d+)/(?P<direction>up|down|clear)vote/?$', vote_on_object, act_dict),
)
