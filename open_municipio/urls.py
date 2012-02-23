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

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.contrib.auth.decorators import login_required
from django.contrib.comments.models import Comment
from django.contrib.comments.views import comments
from django.views.generic.base import RedirectView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from open_municipio.acts.models import Act
from open_municipio.acts.views import ActDetailView
from open_municipio.om_comments.models import CommentWithMood
from open_municipio.om_comments.views import delete_own_comment
from open_municipio.people.models import Institution, Office, Company, Person
from open_municipio.people.views import InstitutionDetailView
from open_municipio.views import HomeView, InfoView
from voting.views import vote_on_object

from django.contrib.comments.views.comments import post_comment
from django.contrib.comments.views.comments import comment_done


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

  url(r'^istituzioni/', ListView.as_view(model=Institution, template_name='institution_list.html'), {}, name="institution_list"),
  
  url(r'^istituzioni/(?P<slug>[-\w]+)/$', InstitutionDetailView.as_view(template_name='institution_detail.html'), {}, name="institution_detail"),
    
  (r'^uffici/$', ListView.as_view(
    model=Office,
    template_name='office_list.html'
  )), 
  (r'^aziende/$', ListView.as_view(
    model=Company,
    template_name='company_list.html'
  )),

  (r'^atti/$', ListView.as_view(
    model=Act,
    template_name='act_list.html'
  )),
  (r'^atti/(?P<pk>[-\w]+)/$', ActDetailView.as_view(
    model=Act,
    template_name='act_detail.html')),

  # We insert our own post_comment and comment_done urls so to wrap
  # them inside the login_required decorator. We do need that
  # decorator so that only authenticated users can post comments.
  (r'^comments/post/$', login_required(post_comment), 'comments-post-comment'),
  (r'^comments/posted/$', login_required(comment_done), 'comments-comment-done'),
  # Despite the previous urls entries, also standard
  # django.contrib.comments urls must be included. If not, we get some
  # complaints about comment_form_target no reverse match.
  (r'^comments/', include('django.contrib.comments.urls')),
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
   (r'^commenti/(?P<object_id>\d+)/delete/?$', delete_own_comment, comment_dict),
)
