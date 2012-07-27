# -*- mode: python -*-
import os, sys, site

# these constants depend on how the server machine is set-up
DOMAIN_ROOT = '/home/open_municipio/xxx.openmunicipio.it'
PROJECT_ROOT_PARENT = os.path.join(DOMAIN_ROOT, 'private')
SITE_PACKAGES = os.path.join(DOMAIN_ROOT, 'private', 'venv/lib/python2.6/site-packages')

## general setup logic                                                                                                                                      
# add virtualenv's ``site-packages`` dir to the Python path                                                                                                 
site.addsitedir(SITE_PACKAGES)
# prepend ``PROJECT_ROOT_PARENT`` to the Python path
if PROJECT_ROOT_PARENT not in sys.path:
   sys.path.insert(0, PROJECT_ROOT_PARENT)

# required for Django to work !                                                                                                                             
os.environ['DJANGO_SETTINGS_MODULE'] = 'open_xxx.settings_staging'

# create the WSGI application object                                                                                                                        
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
