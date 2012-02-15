from django.conf.urls.defaults import *
from django.views.generic import ListView

from open_municipio.people.models import Company


urlpatterns = patterns('',
    url(r'^$', ListView.as_view(
           model=Company,
           template_name='company_list.html'
  ), name='om_company_list')
)