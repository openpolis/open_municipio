## -*- mode: python -*-
## Use this module as the root URLconf for development
from open_municipio.urls import *

from django.conf import settings
from django.contrib import databrowse
from open_municipio.acts.models import Deliberation
from open_municipio.newscache.models import News

databrowse.site.register(Deliberation)
databrowse.site.register(News)

urlpatterns += patterns('',
    (r'^databrowse/(.*)', databrowse.site.root),
)
