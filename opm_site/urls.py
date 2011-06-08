from django.conf import settings
from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from om.models import Institution, Office, Company, Person
from django.views.generic.base import RedirectView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from views import InstitutionDetailView, HomeView, InfoView

urlpatterns = patterns('',
  (r'^api/1.0/', include('om.api.urls')),

  (r'^admin/doc/', include('django.contrib.admindocs.urls')),
  (r'^admin/', include(admin.site.urls)),

  (r'^js/(?P<path>.*)$', 'django.views.static.serve',
    { 'document_root': '%s/templates/static/js' % settings.BASE_DIR}),
  (r'^css/(?P<path>.*)$', 'django.views.static.serve',
    { 'document_root': '%s/templates/static/css' % settings.BASE_DIR}),
  (r'^images/(?P<path>.*)$', 'django.views.static.serve',
    { 'document_root': '%s/templates/static/images' % settings.BASE_DIR}),
  (r'^fonts/(?P<path>.*)$', 'django.views.static.serve',
    { 'document_root': '%s/templates/static/fonts' % settings.BASE_DIR}),

  # home page
  (r'^$', HomeView.as_view()),  
  
  # info page
  (r'^info.html$', InfoView.as_view()),  

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

)
