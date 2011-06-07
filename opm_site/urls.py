from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from om.models import Institution, Office, Company, Person
from django.views.generic.base import RedirectView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from views import InstitutionDetailView

urlpatterns = patterns('',
  (r'^api/1.0/', include('om.api.urls')),

  (r'^admin/doc/', include('django.contrib.admindocs.urls')),
  (r'^admin/', include(admin.site.urls)),

  (r'^js/(?P<path>.*)$', 'django.views.static.serve',
    { 'document_root': '/Users/guglielmo/Workspace/open_municipio/opm_site/templates/js' }),
  (r'^css/(?P<path>.*)$', 'django.views.static.serve',
    { 'document_root': '/Users/guglielmo/Workspace/open_municipio/opm_site/templates/css'}),
  (r'^images/(?P<path>.*)$', 'django.views.static.serve',
    { 'document_root': '/Users/guglielmo/Workspace/open_municipio/opm_site/templates/images'}),
  (r'^fonts/(?P<path>.*)$', 'django.views.static.serve',
    { 'document_root': '/Users/guglielmo/Workspace/open_municipio/opm_site/templates/fonts'}),

  # home page
  (r'^$', RedirectView.as_view(
    url='/home',
    permanent=True
  )),

  (r'^persone/(?P<slug>[-\w]+).html$', DetailView.as_view(
    model=Person,
    context_object_name='person',
    template_name='person.html')),

  (r'^istituzioni.html$', ListView.as_view(
    model=Institution,
    template_name='institutions_list.html'
  )),
  (r'^istituzioni/(?P<slug>[-\w]+).html$', InstitutionDetailView.as_view(
    template_name='institution.html')),
    
  (r'^uffici.html$', ListView.as_view(
    model=Office,
    template_name='offices_list.html'
  )), 
  (r'^aziende.html$', ListView.as_view(
    model=Company,
    template_name='companies_list.html'
  )),

  (r'', include('django.contrib.flatpages.urls')),

)
