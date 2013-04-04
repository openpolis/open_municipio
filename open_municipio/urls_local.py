## -*- mode: python -*-

# Use this module as the root URLconf for development
# (media and static files server with static.serve views)
# DO NOT USE IN PRODUCTION
from open_municipio.urls import *
from django.conf import settings


urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
)