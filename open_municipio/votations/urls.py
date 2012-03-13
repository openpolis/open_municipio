from django.conf.urls.defaults import *
from django.views.generic import ListView, TemplateView
from open_municipio.votations.models import Votation



urlpatterns = patterns('',
    url(r'^$', ListView.as_view(model=Votation,),  name='om_votation_list'),
    url(r'^(\d+)/$', TemplateView.as_view(template_name="votations/votation_detail.html"),  name='om_votation_detail'),
)
