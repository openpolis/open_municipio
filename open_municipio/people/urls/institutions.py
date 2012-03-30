from django.conf.urls.defaults import *
from django.views.generic import ListView, TemplateView

from open_municipio.people.models import Institution
from open_municipio.people.views import CouncilView, CityGovernmentView

urlpatterns = patterns('',
    url(r'^$', ListView.as_view(
           model=Institution,
           template_name='institution_list.html'
        ), name='om_institution_list'),

    url(r'^mayor/$', 'open_municipio.people.views.show_mayor' , name='om_institution_mayor'),
    url(r'^committee/$', TemplateView.as_view(template_name='people/institution_committee.html') , name='om_institution_committee'),
    url(r'^city-government/$', CityGovernmentView.as_view(), name='om_institution_citigov'),
    url(r'^council/$', CouncilView.as_view(), name='om_institution_council'),


)
