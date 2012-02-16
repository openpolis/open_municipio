from django.conf.urls.defaults import *

from open_municipio.acts.views import ActDetailView


urlpatterns = patterns('',
    url(r'^(?P<pk>\d+)/$', ActDetailView.as_view(),  name='om_act_detail')
)