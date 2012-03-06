from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^mr/(\d+)/(.+)/$', 'django.contrib.contenttypes.views.shortcut', name='monitoring-url-redirect'),
)
