## -*- mode: python -*-
"""
Starter fabfile for deploying a Django-powered web application.

All the settings marked with ``CHANGEME`` MUST be changed to reflect
project-specific setup.  Other settings MAY be changed, but their values should be
generic enough to provide for sensible defaults.
"""

from fabric.api import *
from fabric.context_managers import cd, lcd, settings

from fabfile import code, database as db, venv, static, webserver

import os

# Python interpreter executable to use on virtualenv creation
PYTHON_BIN = 'python2.6' ## CHANGEME!
PYTHON_PREFIX = '' # e.g. ``/usr``, ``/usr/local``; leave empty for default.
PYTHON_FULL_PATH = "%s/bin/%s" % (PYTHON_PREFIX, PYTHON_BIN) if PYTHON_PREFIX else PYTHON_BIN

# exclude patterns for ``rsync`` invocations
RSYNC_EXCLUDE = ( 
    ##CHANGEME!
    '*~',
    '.git',
    '.gitignore',
    '*.pyc',
    '*.sample',
    '*.db',
    'docs/',
    '*.markdown',
    'fabfile.py',
    'bootstrap.py',
    'apache/*',
    'open_municipio/settings_*.py',
    'open_municipio/urls_*.py',
    'open_municipio/sitestatic',
)

## TODO: these constants should be read from an external configuration file
# the name of the project managed by this fabfile
PROJECT_NAME = 'open_municipio' 
# a unique identifier for this web application instance
# usually is set to the primary domain from which the web application is accessed
APP_DOMAIN = 'www.example.com' 
# filesystem location of project's files on the local machine
LOCAL_PROJECT_ROOT = '/local/path/to/open_municipio'

env.project = PROJECT_NAME
env.app_domain = APP_DOMAIN
env.local_project_root = LOCAL_PROJECT_ROOT

## Environment-specific setup
@task
def staging():
    """ Use staging environment on remote host"""
    env.environment = 'staging'
    ## TODO: these constants should be read from an external configuration file
    # the system user (on the server machine) used for managing websites
    WEB_USER = 'webuser' ##CHANGEME!
    # the parent directory of domain-specific directories (on the server machine) 
    WEB_ROOT = os.path.join('/home', WEB_USER, 'websites') 
    # the root directory for domain-specific files (on the server machine)
    DOMAIN_ROOT = os.path.join(WEB_ROOT, env.app_domain) 
    # the root directory of application-specific Python virtual environment (on the server machine)
    VIRTUALENV_ROOT = os.path.join(DOMAIN_ROOT, 'private', 'venv') 
    # the root directory for project-specific files (on the server machine)
    PROJECT_ROOT = os.path.join(DOMAIN_ROOT, 'private', env.project) 
    # the root directory for application-specific Python code (on the server machine)
    CODE_ROOT = os.path.join(PROJECT_ROOT, env.project) ##CHANGEME!
    # import path of Django settings file for the staging environment
    DJANGO_SETTINGS_MODULE = '%(project)s.settings_staging' % env 
    # Directory where static files should be collected.  This MUST equal the value
    # of ``STATIC_ROOT`` attribute of the Django settings module used on the server.
    STATIC_ROOT =  os.path.join(DOMAIN_ROOT, 'public', 'static') ## CHANGEME!
    ## set up Fabric global environment dictionary
    env.web_user = WEB_USER
    env.web_root = WEB_ROOT
    env.domain_root = DOMAIN_ROOT
    env.virtualenv_root = VIRTUALENV_ROOT
    env.project_root = PROJECT_ROOT
    env.code_root = CODE_ROOT
    env.settings = DJANGO_SETTINGS_MODULE
    env.static_root = STATIC_ROOT
    
    env.roledefs = {
    'web': ['webuser@www.example.com'],
    'db': ['dbuser@db.example.com'],
    }
 
@task
def production():
    """ Use production environment on remote host"""
    env.environment = 'production'
    utils.abort('Production deployment not yet implemented.')


## Macro-tasks
@task
@roles('web')
def initial_deploy():
    """
    Deploy the web application to remote server(s) **for the first time**

    The first deployment procedure may differ from subsequent ones,
    since some initialization tasks have to be performed only once.

    Some examples:
    * fake South migrations
    * ..
    """
    require('environment', provided_by=('staging', 'production'))
    env.initial_deploy = True
    deploy()        

@task
@roles('web')
def deploy():
    """
    Deploy the web application to remote server(s)
    """
    require('environment', provided_by=('staging', 'production'))
    ## TODO: early initialization steps go here  
    if env.get('initial_deploy'):
        code.copy_website_skeleton()

    with settings(warn_only=True):
        webserver.stop()

    code.update()
    venv.update_requirements()
    db.update()
    static.collect_files()
    adjust_permissions()
    webserver.clear_logs()

    webserver.start()


def adjust_permissions():
    """
    Adjust filesystem permissions after completing the deployment process.
    """
    require('web_user', 'domain_root', 'code_root', provided_by=('staging', 'production'))
    sudo('chown -R %(web_user)s:www-data %(domain_root)s' % env)
    ## Only needed for SQLite DBs
    # SQLite need write access to the folder containing the DB file
    sudo('chmod g+w %(code_root)s' % env)
    # SQLite need write access to the DB file itself
    db_file = os.path.join(env.code_root, 'sqlite.db')
    sudo('chmod g+w %s' % db_file)


