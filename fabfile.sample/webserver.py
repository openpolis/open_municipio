from fabric.api import *
from fabric.context_managers import cd, lcd, settings

import os


## Webserver management
@task
def reload():    
    """
    Reload the webserver on remote host
    """
    sudo('/etc/init.d/apache2 reload')

@task
def start():    
    """
    Start the webserver on remote host
    """
    sudo('/etc/init.d/apache2 start')

@task
def stop():    
    """
    Restart the webserver on remote host
    """
    sudo('/etc/init.d/apache2 stop')

@task
def restart():    
    """
    Restart the webserver on remote host
    """
    sudo('/etc/init.d/apache2 restart')

@task
def enable_site(site_name):
    """
    Enable a webserver virtualhost
    """
    sudo('a2ensite %s' % site_name)

@task
def disable_site(site_name):
    """
    Disable a webserver virtualhost
    """
    sudo('a2dissite %s' % site_name)

@task
def upload_conf():
    """
    Upload webserver configuration to remote host
    """
    require('environment', provided_by=('staging', 'production'))
    ## upload custom Apache directives
    source = os.path.join(env.local_project_root, 'apache', 'httpd.conf.%(environment)s' % env)
    with cd('/etc/apache2'):
        dest = 'httpd.conf'
        put(source, dest, use_sudo=True, mode=0644)
        sudo('chown root:root %s' % dest)
    ## upload Virtual Host configuration
    source = os.path.join(env.local_project_root, 'apache', 'vhost.conf.%(environment)s' % env)
    with cd('/etc/apache2/sites-available'):
        dest = env.app_domain
        put(source, dest, use_sudo=True, mode=0644)
        sudo('chown root:root %s' % dest)

@task  
def update_conf():
    """Update webserver configuration on remote host """
    upload_conf()
    enable_site(env.app_domain)
    restart()

@task
def touch_WSGI_script():
    """ Touch WSGI file to trigger code reload """
    require('project_root', provided_by=('staging', 'production'))
    apache_dir = os.path.join(env.project_root, 'apache')
    with cd(apache_dir):
        run('touch django.wsgi')

@task
def clear_logs():
    """
    Clear website-specific logs.
    """
    require('domain_root', provided_by=('staging', 'production'))
    with cd(env.domain_root):
        run('rm -f log/*')
