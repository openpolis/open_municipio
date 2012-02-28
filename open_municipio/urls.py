## Global URLconf module for the "OpenMunicipio" web application.
##
## Since some URL patterns may be machine-specific (think about static files served
## by Django in development setups), it's advisable to keep those URL patterns
## within a separate URLconf module, beginning with this import statement:
##
## .. code:: python
##
##     from open_municipio.urls import * 
##
## This way, project-level URL patterns are transparently added to 
## machine-specific ones.
##
## A common naming scheme for these "overlay" URLconf modules is as follows:
##
## * ``urls_local.py`` -- for development machines
## * ``urls_staging.py`` -- for staging servers
## * ``urls_production.py`` -- for production servers


from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

from voting.views import vote_on_object

from open_municipio.views import HomeView, InfoView
from open_municipio.acts.models import Act
from open_municipio.om_comments.models import CommentWithMood

from open_municipio.inline_edit.views import InlineEditView


urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),

  # home page
  (r'^$', HomeView.as_view()),  
  
  # info page
  (r'^info/$', InfoView.as_view()),  

  (r'^comments/', include('django.contrib.comments.urls')),

  (r'^people/', include('open_municipio.people.urls.people')),
  (r'^institutions/', include('open_municipio.people.urls.institutions')),
  (r'^offices/', include('open_municipio.people.urls.offices')),
  (r'^companies/', include('open_municipio.people.urls.companies')), 
  (r'^acts/', include('open_municipio.acts.urls')),

)


act_dict = {
    'model': Act,
    'template_object_name': 'act',
    'allow_xmlhttprequest': 'true',
}

comment_dict = {
    'model': CommentWithMood,
    'template_object_name': 'comment',
    'allow_xmlhttprequest': 'true',
}

urlpatterns += patterns('',
   (r'^atti/(?P<object_id>\d+)/(?P<direction>up|down|clear)vote/?$', vote_on_object, act_dict),
   (r'^commenti/(?P<object_id>\d+)/(?P<direction>up|down|clear)vote/?$', vote_on_object, comment_dict),
)

# inline editing
urlpatterns += patterns('',
    url(r'^inline/edit/$', InlineEditView.as_view(),  name='om_inline_edit'),
)
