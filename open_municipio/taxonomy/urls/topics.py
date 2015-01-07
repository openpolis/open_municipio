from django.conf.urls.defaults import *
from django.views.decorators.cache import cache_page

from open_municipio.taxonomy.views import TopicListView


urlpatterns = patterns('',
    url(r'^$', cache_page(60 * 720)(TopicListView.as_view()), name='om_topic_list'),
)

