# -*- mode: python -*-
import os, sys, site

# these constants depend on how the server machine is setup                                                                                                 
DOMAIN_ROOT = '/path/to/domain/root'
PROJECT_ROOT = os.path.join(DOMAIN_ROOT, 'private', 'open_municipio')
SITE_PACKAGES = os.path.join(DOMAIN_ROOT, 'private', 'venv/lib/python2.6/site-packages')

## general setup logic                                                                                                                                      
# add virtualenv's ``site-packages`` dir to the Python path                                                                                                 
site.addsitedir(SITE_PACKAGES)
# prepend ``PROJECT_ROOT`` to the Python path                                                                                                               
if PROJECT_ROOT not in sys.path:
   sys.path.insert(0, PROJECT_ROOT)

# required for Django to work !                                                                                                                             
os.environ['DJANGO_SETTINGS_MODULE'] = 'open_municipio.settings_production'

# create the WSGI application object                                                                                                                        
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()



