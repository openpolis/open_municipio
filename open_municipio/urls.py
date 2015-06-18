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

from registration.views import register

from open_municipio.om.views import ( HomeView, ContactsView, ConditionsView, \
                                PrivacyView, server_error )
from open_municipio.inline_edit.views import InlineEditView
from open_municipio.om_auth.views import login_done, login_error, login_form, logout
from open_municipio.users.forms import UserRegistrationForm

admin.autodiscover()

handler500 = 'open_municipio.om.views.server_error'

urlpatterns = patterns('',
    url(r'^500/$', server_error, name='om_error_500'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),   
    # home page
    url(r'^$', HomeView.as_view(), name="home"),
    # info page
    url(r'^contatti/$', ContactsView.as_view(), name='om_contatti'),
    url(r'^progetto/$', TemplateView.as_view(template_name='om/info.html'), name='om_progetto'),
    url(r'^regolamento/$', TemplateView.as_view(template_name='om/rules.html'), name='om_regolamento'),
    url(r'^condizioni/$', ConditionsView.as_view(), name='om_condizioni'),
    url(r'^privacy/$', PrivacyView.as_view(), name='om_privacy'),
    url(r'^opendata/$', TemplateView.as_view(template_name='om/opendata.html'), name='om_opendata'),
    url(r'^software/$', TemplateView.as_view(template_name='om/software.html'), name='om_software'),
    url(r'^registrarsi/$', TemplateView.as_view(template_name='om/registrarsi.html'), name='om_registrarsi'),
    url(r'^monitorare/$', TemplateView.as_view(template_name='om/monitorare.html'), name='om_monitorare'),
    url(r'^votare/$', TemplateView.as_view(template_name='om/votare.html'), name='om_votare'),
    url(r'^domande/$', TemplateView.as_view(template_name='om/domande.html'), name='om_domande'),
    url(r'^comments/', include('open_municipio.om_comments.urls')),
    url(r'^people/', include('open_municipio.people.urls.people')),
    url(r'^institutions/', include('open_municipio.people.urls.institutions')),
    url(r'^offices/', include('open_municipio.people.urls.offices')),
    url(r'^companies/', include('open_municipio.people.urls.companies')), 
    url(r'^sittings/', include('open_municipio.people.urls.sittings')),
    url(r'^acts/', include('open_municipio.acts.urls')),
    url(r'^votations/', include('open_municipio.votations.urls')),
    url(r'^attendances/', include('open_municipio.attendances.urls')),
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

# user registration, authentication and profiles
urlpatterns += patterns('',
    url(r'^accounts/register/$', register, {
            'backend': 'registration.backends.default.DefaultBackend',
            'form_class': UserRegistrationForm
            }, name='registration_register'),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^users/', include('open_municipio.users.urls')),
    url(r'^login-done/$', login_done, name='login-done'),
    url(r'^login-error/$', login_error, name='login-error'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^login-form/$', login_form, name='login-form'),
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
