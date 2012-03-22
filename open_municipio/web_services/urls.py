from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^share/(?P<app>\w+)/(?P<model>\w+)/(?P<object_id>\d+)/', 'open_municipio.web_services.views.share', name="web_service_share"),
)
