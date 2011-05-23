from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
  # (r'^/', include('om.urls')),

  # Uncomment the next line to enable the admin:
  (r'^admin/', include(admin.site.urls)),

  (r'^js/(?P<path>.*)$', 'django.views.static.serve',
    { 'document_root': '/Users/guglielmo/Workspace/open_municipio/opm_site/templates/js' }),
  (r'^css/(?P<path>.*)$', 'django.views.static.serve',
    { 'document_root': '/Users/guglielmo/Workspace/open_municipio/opm_site/templates/css'}),
  (r'^images/(?P<path>.*)$', 'django.views.static.serve',
    { 'document_root': '/Users/guglielmo/Workspace/open_municipio/opm_site/templates/images'}),
  (r'^fonts/(?P<path>.*)$', 'django.views.static.serve',
    { 'document_root': '/Users/guglielmo/Workspace/open_municipio/opm_site/templates/fonts'}),


  (r'', include('django.contrib.flatpages.urls')),

)
