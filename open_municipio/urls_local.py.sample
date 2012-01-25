## -*- mode: python -*-
## Use this module as the root URLconf for development

from open_municipio.urls import *

urlpatterns += patterns('',
  (r'^js/(?P<path>.*)$', 'django.views.static.serve',
    { 'document_root': '%s/templates/static/js' % settings.PROJECT_ROOT}),
  (r'^css/(?P<path>.*)$', 'django.views.static.serve',
    { 'document_root': '%s/templates/static/css' % settings.PROJECT_ROOT}),
  (r'^images/(?P<path>.*)$', 'django.views.static.serve',
    { 'document_root': '%s/templates/static/images' % settings.PROJECT_ROOT}),
  (r'^fonts/(?P<path>.*)$', 'django.views.static.serve',
    { 'document_root': '%s/templates/static/fonts' % settings.PROJECT_ROOT}),
)
