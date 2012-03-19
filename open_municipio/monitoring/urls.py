from django.conf.urls.defaults import *

from django.contrib.contenttypes.views import shortcut

from open_municipio.monitoring.views import start, stop

urlpatterns = patterns('',
    url(r'^start/', start, name='om_monitoring_start'),
    url(r'^stop/', stop, name='om_monitoring_stop'),
    url(r'^mr/(?P<content_type_id>\d+)/(?P<object_pk>\d+)/$', shortcut, name='om_monitoring_url_redirect'),
)
