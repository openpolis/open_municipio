from django.conf.urls.defaults import *
from django.views.generic import ListView

from open_municipio.people.models import Institution
from open_municipio.people.views import InstitutionDetailView

urlpatterns = patterns('',
    url(r'^$', ListView.as_view(
           model=Institution,
           template_name='institution_list.html'
        ), name='om_institution_list'),
  
    url(r'^(?P<slug>[-\w]+)/$', InstitutionDetailView.as_view(
           template_name='institution_detail.html'
        ), name='om_institution_detail'),
)
    