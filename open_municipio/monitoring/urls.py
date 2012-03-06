from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^start/', 'open_municipio.monitoring.views.start', name="monitoring-start"),
    url(r'^stop/', 'open_municipio.monitoring.views.stop', name="monitoring-stop"),
    url(r'^mr/(\d+)/(.+)/$', 'django.contrib.contenttypes.views.shortcut', name='monitoring-url-redirect'),
)
