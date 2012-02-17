from fabric.api import *
from fabric.context_managers import cd, lcd, settings
from fabric import utils
from fabric.contrib import files, console
from fabric.contrib.project import rsync_project

from fabfile.webserver import touch_WSGI_script

import os

## Application code management
@task
def copy_website_skeleton():
    """
    Create a skeleton directory tree for the new website.

    Include setup of suitable filesystem permissions.
    """
    require('web_root', 'app_domain', provided_by=('staging', 'production'))
    with cd(env.web_root):
        if files.exists(env.app_domain):
            utils.abort("Directory %s already exists on the remote machine" % os.path.join(env.web_root, env.app_domain))
        run('cp -a skeleton %(app_domain)s' % env) 

@task
def update():
    """Transfer application code to remote host"""
    require('project_root', 'code_root', provided_by=('staging', 'production'))
    from fabfile import RSYNC_EXCLUDE
    if env.environment == 'production':
        if not console.confirm('Are you sure you want to deploy to the production server(s)?',
                               default=False):
            utils.abort('Production deployment aborted.')
    # defaults rsync options:
    # -pthrvz
    # -p preserve permissions
    # -t preserve times
    # -h output numbers in a human-readable format
    # -r recurse into directories
    # -v increase verbosity
    # -z compress file data during the transfer
    extra_opts = '--omit-dir-times'
    rsync_project(
        remote_dir = env.project_root,
        local_dir = env.local_project_root + os.path.sep,
        exclude=RSYNC_EXCLUDE,
        delete=True,
        extra_opts=extra_opts,
    )
    
    with lcd(os.path.join(env.local_project_root, env.project)):
        with cd(env.code_root):
            # update Django settings module
            settings_file = 'settings_%(environment)s.py' % env
            put(settings_file, settings_file, mode=0644)
            # update Django main URLconf module
            urls_file = 'urls_%(environment)s.py' % env        
            put(urls_file, urls_file, mode=0644)

    with lcd(os.path.join(env.local_project_root, 'apache')):
        with cd(os.path.join(env.project_root, 'apache')):
            source = '%(environment)s.wsgi' % env
            dest = 'django.wsgi'
            put(source, dest, mode=0644)

    # trigger code reloading
    touch_WSGI_script()
