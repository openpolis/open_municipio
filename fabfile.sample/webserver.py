from fabric.api import cd, env, execute, hide, put, require, roles, run, sudo, task
from fabric.utils import fastprint

import os


## Webserver management
@task
@roles('web')
def reload():    
    """
    Reload the webserver on the remote host.
    """
    with hide('stdout', 'running'):
        fastprint("Reloading Apache webserver..." % env, show_prefix=True)
        sudo('/etc/init.d/apache2 reload')
        fastprint(" done." % env, end='\n')


@task
@roles('web')
def start():    
    """
    Start the webserver on the remote host.
    """
    with hide('stdout', 'running'):
        fastprint("Starting Apache webserver..." % env, show_prefix=True)
        sudo('/etc/init.d/apache2 start')
        fastprint(" done." % env, end='\n')  


@task
@roles('web')
def stop():    
    """
    Stop the webserver on the remote host.
    """
    with hide('stdout', 'running'):
        fastprint("Stopping Apache webserver..." % env, show_prefix=True)
        sudo('/etc/init.d/apache2 stop')
        fastprint(" done." % env, end='\n')  


@task
@roles('web')
def restart():    
    """
    Restart the webserver on the remote host.
    """
    with hide('stdout', 'running'):
        fastprint("Restarting Apache webserver...", show_prefix=True)
        sudo('/etc/init.d/apache2 restart')
        fastprint(" done." % env, end='\n')  


@task
@roles('om')
def enable_site(site_name):
    """
    Enable a webserver's virtualhost.
    """
    with hide('stdout', 'running'):
        fastprint("Enabling site %s..." % site_name, show_prefix=True)
        sudo('a2ensite %s' % site_name)
        fastprint(" done." % env, end='\n')  
  

@task
@roles('om')
def disable_site(site_name):
    """
    Disable a webserver's virtualhost.
    """
    with hide('stdout', 'running'):
        fastprint("Disabling site %s..." % site_name, show_prefix=True)
        sudo('a2dissite %s' % site_name)
        fastprint(" done." % env, end='\n')  
      

@task
@roles('om')
def upload_conf():
    """
    Upload webserver configuration to the remote host.
    """
    require('environment', provided_by=('staging', 'production'))
    ## upload custom Apache directives
    fastprint("Uploading vhost configuration for %(app_domain)s..." % env, show_prefix=True)
    with hide('stdout', 'running'):
        source = os.path.join(env.local_repo_root, 'apache', 'httpd.conf.%(environment)s' % env)
        with cd('/etc/apache2'):
            dest = 'httpd.conf'
            put(source, dest, use_sudo=True, mode=0644)
            sudo('chown root:root %s' % dest)
        ## upload Virtual Host configuration
        source = os.path.join(env.local_repo_root, 'apache', 'vhost.conf.%(environment)s' % env)
        with cd('/etc/apache2/sites-available'):
            dest = env.app_domain
            put(source, dest, use_sudo=True, mode=0644)
            sudo('chown root:root %s' % dest)
    fastprint(" done." % env, end='\n')
    
    
@task 
@roles('om')
def update_conf():
    """
    Update webserver configuration on the remote host.
    """
    execute(upload_conf)
    execute(enable_site, site_name=env.app_domain)

@task
@roles('om')
def touch_WSGI_script():
    """
    Touch WSGI script to trigger code reload.
    """
    require('domain_root', provided_by=('staging', 'production'))
    fastprint("Triggering code reload..." % env, show_prefix=True)
    with hide('stdout', 'running'):
        apache_dir = os.path.join(env.domain_root, 'private', 'apache')
        with cd(apache_dir):
            run('touch django.wsgi')
    fastprint(" done." % env, end='\n')
    
    
@task
@roles('om')
def clear_logs():
    """
    Clear website-specific logs.
    """
    require('domain_root', provided_by=('staging', 'production'))
    fastprint("Clearing old webserver logs..." % env, show_prefix=True)
    with hide('stdout', 'running'):
        with cd(env.domain_root):
            run('rm -f log/*')
    fastprint(" done." % env, end='\n')