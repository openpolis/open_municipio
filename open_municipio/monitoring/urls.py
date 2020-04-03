from django.conf.urls import *
from django.contrib.auth.decorators import login_required

from django.contrib.contenttypes.views import shortcut

from open_municipio.monitoring.views import MonitoringStartView, MonitoringStopView

urlpatterns = patterns('',
    url(r'^start/', login_required(MonitoringStartView.as_view()), name='om_monitoring_start'),
    url(r'^stop/', login_required(MonitoringStopView.as_view()), name='om_monitoring_stop'),
    url(r'^mr/(?P<content_type_id>\d+)/(?P<object_pk>\d+)/$', shortcut, name='om_monitoring_url_redirect'),
)
