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


from django.conf.urls.defaults import patterns, url, include
from django.views.generic import TemplateView

from django.contrib import admin
from open_municipio.om.views import HomeView
from open_municipio.inline_edit.views import InlineEditView


admin.autodiscover()


urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),   
    # home page
    url(r'^$', HomeView.as_view()),
    # info page
    url(r'^info/$', TemplateView.as_view(template_name='om/info.html')),
    url(r'^rules/$', TemplateView.as_view(template_name='om/rules.html'), name='om_rules'),
    url(r'^terms-and-conditions/$', TemplateView.as_view(template_name='om/terms-and-conditions.html'), name='om_terms'),
    url(r'^privacy/$', TemplateView.as_view(template_name='om/privacy.html'), name='om_privacy'),
    url(r'^comments/', include('open_municipio.om_comments.urls')),
    url(r'^people/', include('open_municipio.people.urls.people')),
    url(r'^institutions/', include('open_municipio.people.urls.institutions')),
    url(r'^offices/', include('open_municipio.people.urls.offices')),
    url(r'^companies/', include('open_municipio.people.urls.companies')), 
    url(r'^acts/', include('open_municipio.acts.urls')),
    url(r'^votations/', include('open_municipio.votations.urls')),
    url(r'^topics/', include('open_municipio.taxonomy.urls.topics')),
    url(r'^categories/', include('open_municipio.taxonomy.urls.categories')),
    url(r'^tags/', include('open_municipio.taxonomy.urls.tags')),
    url(r'^locations/', include('open_municipio.locations.urls')),
    url(r'^webservices/', include('open_municipio.web_services.urls')),
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
    url(r'', include('social_auth.urls')),
)

# search test
urlpatterns += patterns('',
    url(r'^search/', include('haystack.urls')),
)

# bookmarking
urlpatterns += patterns('',
    url(r'^bookmark/', include('open_municipio.bookmarking.urls')),
)
