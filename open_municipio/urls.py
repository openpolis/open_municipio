## Global URLconf module for the "OpenMunicipio" web application.
##
## Since some URL patterns may be machine-specific (think about static files served
## by Django in development setups), it's advisable to keep those URL patterns
## within a separate URLconf module, beginning with this import statement:
##
## .. code:: python
##
##     from opm_site.urls import * 
##
## This way, project-level URL patterns are transparently added to 
## machine-specific ones.
##
## A common naming scheme for these "overlay" URLconf modules is as follows:
##
## * ``urls_local.py`` -- for development machines
## * ``urls_staging.py`` -- for staging servers
## * ``urls_production.py`` -- for production servers


from django.conf import settings
from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from open_municipio.om.models import Institution, Office, Company, Person
from django.views.generic.base import RedirectView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from open_municipio.views import InstitutionDetailView, HomeView, InfoView

urlpatterns = patterns('',
  (r'^admin/doc/', include('django.contrib.admindocs.urls')),
  (r'^admin/', include(admin.site.urls)),

  # home page
  (r'^$', HomeView.as_view()),  
  
  # info page
  (r'^info/$', InfoView.as_view()),  

  (r'^persone/(?P<slug>[-\w]+)/$', DetailView.as_view(
    model=Person,
    context_object_name='person',
    template_name='person_detail.html')),

  (r'^istituzioni/$', ListView.as_view(
    model=Institution,
    template_name='institution_list.html'
  )),
  (r'^istituzioni/(?P<slug>[-\w]+)/$', InstitutionDetailView.as_view(
    template_name='institution_detail.html')),
    
  (r'^uffici/$', ListView.as_view(
    model=Office,
    template_name='office_list.html'
  )), 
  (r'^aziende/$', ListView.as_view(
    model=Company,
    template_name='company_list.html'
  )),

)
