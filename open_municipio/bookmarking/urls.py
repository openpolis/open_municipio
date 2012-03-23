from django.conf.urls.defaults import *

from open_municipio.bookmarking.views import ToggleBookmarkView

urlpatterns = patterns('',
    url(r'(?P<app_label>\w+)/(?P<model_name>\w+)/(?P<obj_pk>\d+)/toggle/$', ToggleBookmarkView.as_view(), name='om_bookmark_toggle'),
)

