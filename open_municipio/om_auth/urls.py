from django.conf import settings
from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from registration.views import register

from open_municipio.om_auth.views import home, done, logout, error, form
from open_municipio.users.forms import UserRegistrationForm
import open_municipio.users.regbackend


admin.autodiscover()

urlpatterns = patterns('',
#    url(r'^accounts/register/$', register, {
#            'backend': 'registration.backends.default.DefaultBackend',
#            'form_class': UserRegistrationForm
#            }, name='registration_register'),
    url(r'^done/$', done, name='done'),
    url(r'^error/$', error, name='error'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^form/$', form, name='form'),
    )

#if settings.DEBUG:
#    urlpatterns += staticfiles_urlpatterns()
