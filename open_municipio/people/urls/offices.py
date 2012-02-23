from django.conf.urls.defaults import *
from django.views.generic import ListView

from open_municipio.people.models import Office

urlpatterns = patterns('',
    url(r'^$', ListView.as_view(
    model=Office,
    template_name='office_list.html',
  ), name='om_office_list'),
)