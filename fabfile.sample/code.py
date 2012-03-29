from fabric.api import *
from fabric.context_managers import cd, lcd, settings
from fabric import utils
from fabric.contrib import files, console
from fabric.contrib.project import rsync_project

from webserver import touch_WSGI_script

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
            utils.abort("Directory %s already exists on the remote machine" %
                        os.path.join(env.web_root, env.app_domain))
        run('mkdir %(app_domain)s' % env)
        run('mkdir -p %(app_domain)s/backup' % env)
        run('mkdir -p %(app_domain)s/log' % env)
        run('mkdir -p %(app_domain)s/private' % env)
        run('mkdir -p %(app_domain)s/private/python' % env)
        run('mkdir -p %(app_domain)s/private/venv' % env)
        run('mkdir -p %(app_domain)s/public' % env)
        run('mkdir -p %(app_domain)s/public/media' % env)
        run('mkdir -p %(app_domain)s/public/static' % env)

@task
@roles('web')
def update():
    """Transfer application code to remote host"""
    require('project_root', 'code_root', provided_by=('staging', 'production'))
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
        exclude=env.rsync_exclude,
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

            source = 'httpd.conf.%(environment)s' % env
            dest = 'httpd.conf'
            put(source, dest, mode=0644)

            source = 'vhost.conf.%(environment)s' % env
            dest = 'vhost.conf'
            put(source, dest, mode=0644)

    with cd(env.code_root):
        sudo('chmod g+w .')

    # fixtures are copied from test_data into initial_data,
    # so that they are automatically imported by the syncdb command
    # add applications containing fixtures as needed to the list below
    apps_list = ('users', 'people', 'acts', 'votations', 'taxonomy', 'newscache')
    for app in apps_list:
        with lcd(os.path.join(env.local_project_root, 'open_municipio', app, 'fixtures')):
            with cd(os.path.join(env.project_root, 'open_municipio', app, 'fixtures')):
                put('test_data.json', 'initial_data.json', mode=0644)

    # copy fixtures specific for the staging/production enviroment
    apps_list = ('om',)
    for app in apps_list:
        with lcd(os.path.join(env.local_project_root, 'open_municipio', app, 'fixtures')):
            with cd(os.path.join(env.project_root, 'open_municipio', app, 'fixtures')):
                put('test_data_%(environment)s.json' % env, 'initial_data.json', mode=0644)


    # trigger code reloading
    touch_WSGI_script()
