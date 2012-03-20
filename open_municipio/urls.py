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
from voting.views import vote_on_object
from open_municipio.acts.models import Act
from open_municipio.om_comments.models import CommentWithMood
from open_municipio.inline_edit.views import InlineEditView
admin.autodiscover()


urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    
    # home page
    (r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'om/home.html'}),

    # info page
    (r'^info/$', 'django.views.generic.simple.direct_to_template', {'template': 'om/info.html'}),

    (r'^comments/', include('open_municipio.om_comments.urls')),
    (r'^people/', include('open_municipio.people.urls.people')),
    (r'^institutions/', include('open_municipio.people.urls.institutions')),
    (r'^offices/', include('open_municipio.people.urls.offices')),
    (r'^companies/', include('open_municipio.people.urls.companies')), 
    (r'^acts/', include('open_municipio.acts.urls')),
    (r'^voting/', include('open_municipio.votations.urls')),
    (r'^tag/', include('open_municipio.taxonomy.urls')),
)

# inline editing
urlpatterns += patterns('',
    url(r'^inline/edit/$', InlineEditView.as_view(),  name='om_inline_edit'),
)

# autocompletion
urlpatterns += patterns('',
    url(r'^autocomplete/', include('open_municipio.autocomplete.urls')),
)

# monitoring
urlpatterns += patterns('',
    url(r'^monitoring/', include('open_municipio.monitoring.urls')),
)

# user registration and profiles
urlpatterns += patterns('',
    url(r'^accounts/', include('open_municipio.registration.backends.om.urls')),
    url(r'^users/', include('open_municipio.users.urls')),
)

