from django.conf.urls.defaults import *

from open_municipio.bookmarking.views import ToggleBookmarkView

urlpatterns = patterns('',
    url(r'(?P<content_type_id>\d+)/(?P<object_pk>\d+)/toggle/$', ToggleBookmarkView.as_view(), name='om_bookmark_toggle'),
)

