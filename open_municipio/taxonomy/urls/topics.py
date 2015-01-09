from django.conf.urls.defaults import *

from open_municipio.taxonomy.views import TopicListView

urlpatterns = patterns('',
    url(r'^$', TopicListView.as_view(), name='om_topic_list'),
)

