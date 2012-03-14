from django.conf.urls.defaults import *
from django.views.generic import ListView, TemplateView

from open_municipio.people.models import Institution
from open_municipio.people.views import InstitutionDetailView

urlpatterns = patterns('',
    url(r'^$', ListView.as_view(
           model=Institution,
           template_name='institution_list.html'
        ), name='om_institution_list'),

    url(r'^commission/$', TemplateView.as_view(template_name='people/institution_commission.html' ) , name='om_institution_commission'),
    url(r'^city-government/$', TemplateView.as_view(template_name='people/institution_citygov.html' ) , name='om_institution_citigov'),
    url(r'^council/$', TemplateView.as_view(template_name='people/institution_council.html') , name='om_institution_council'),

    url(r'^(?P<slug>[-\w]+)/$', InstitutionDetailView.as_view(
           template_name='institution_detail.html'
        ), name='om_institution_detail'),

)