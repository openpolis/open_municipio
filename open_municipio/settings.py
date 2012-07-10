# -*- coding: utf-8 -*-
# ## Django global settings for the "OpenMunicipio" web application.
##
## Note that machine-specific settings (such as DB connection parameters,
## absolute filesystem paths, passwords, etc.) should be placed within 
## a separate Python module, beginning with this import statement:
##
## .. code:: python
##     from open_municipio.settings import * 
##
## This way, machine-specific settings override project-level settings.
##
## A common naming scheme for these "overlay" settings files is as follows:
##
## * ``settings_local.py`` -- for development machines
## * ``settings_staging.py`` -- for staging servers
## * ``settings_production.py`` -- for production servers

import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
REPO_ROOT = os.path.abspath(os.path.dirname(PROJECT_ROOT))
VERSION = __version__ = file(os.path.join(PROJECT_ROOT, 'VERSION')).read().strip()

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Rome'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'it-IT'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
)


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)


TEMPLATE_DIRS = (
  os.path.join(PROJECT_ROOT, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "open_municipio.om.context_processor.defaults",
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    "social_auth.context_processors.social_auth_by_name_backends",
    "social_auth.context_processors.social_auth_backends",
    "social_auth.context_processors.social_auth_by_type_backends",
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.comments',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.staticfiles',
    'django_extensions',
    'registration',
#    'open_municipio.registration',
    'profiles',
    'south',
    'taggit',
    'voting',
    'open_municipio.events',
    'open_municipio.inline_edit',
    'open_municipio.autocomplete',
    'open_municipio.om',
    'open_municipio.om_comments',
    'open_municipio.om_voting',
    'open_municipio.bookmarking',
    'open_municipio.acts',
    'open_municipio.people',
    'open_municipio.taxonomy',
    'open_municipio.locations',
    'open_municipio.votations',
    'open_municipio.users',
    'open_municipio.monitoring',
    'open_municipio.web_services',
    'open_municipio.newscache',
    'haystack',
    'sorl.thumbnail',
    'social_auth',
    'open_municipio.om_auth',
)

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.facebook.FacebookBackend',
    'social_auth.backends.google.GoogleOAuth2Backend',
    'social_auth.backends.contrib.github.GithubBackend',
    'social_auth.backends.OpenIDBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# ``django-social-auth`` settings
FACEBOOK_EXTENDED_PERMISSIONS = ['email']
LOGIN_URL          = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGIN_ERROR_URL    = '/login-error/'
SOCIAL_AUTH_COMPLETE_URL_NAME  = 'socialauth_complete'
SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'socialauth_associate_complete'
SOCIAL_AUTH_EXPIRATION = 'expires'
SOCIAL_AUTH_RAISE_EXCEPTIONS = DEBUG
SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    'social_auth.backends.pipeline.associate.associate_by_email',
    'social_auth.backends.pipeline.misc.save_status_to_session',
    'om_auth.pipeline.redirect_to_form',
    'om_auth.pipeline.extra_data',
    'social_auth.backends.pipeline.user.create_user',
    'om_auth.pipeline.create_profile',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    'social_auth.backends.pipeline.user.update_user_details',
)

# ``django-registration`` settings
ACCOUNT_ACTIVATION_DAYS = 7 # Activation window
REGISTRATION_AUTO_LOGIN = True

# use app shortcut (app.class)
AUTH_PROFILE_MODULE = 'users.UserProfile'

# comments settings
COMMENTS_APP = 'open_municipio.om_comments'

# external web services configuration
WEB_SERVICES = {
    'google_analytics': { 'code' : 'UA-XXXXXX-YY' },
    'facebook' :        { 'code' : '1234567890' },
    'twitter' : {},
    'google_plus': {},
}

## settings for the ``open_municipio.bookmarking`` app
# CSS class used to mark DOM elements associated with bookmarked (key) objects 
OM_BOOKMARKING_STAR_CLASS = 'icon-star'
# CSS class used to mark DOM elements associated with bookmarkable (but not-key) objects
OM_BOOKMARKING_EMPTY_STAR_CLASS = 'icon-star-empty'

# Site templates globals variables
SITE_INFO = {
    'main_city': u'City',
    'site_version': u'Beta',
    'main_city_logo': 'img/city-logo/city-logo.png'
}

## settings for the ``open_municipio.om_comments`` app
# Number of second within which users can delete their own comments
OM_COMMENTS_REMOVAL_MAX_TIME = 600
