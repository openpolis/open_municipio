from fabric import utils
from fabric.contrib.project import rsync_project
import os
from fabric.api import *
from fabric.contrib import files, console
from fabric.context_managers import cd

from venv import run_venv

## Solr management

@task
@roles('web')
def restart_tomcat():
    require('tomcat_controller', provided_by=('staging', 'production'))
    sudo('%(tomcat_controller)s restart' % env)

@task
@roles('web')
def make_common_skeleton():
    """
    Create a skeleton directory tree for the solr application
    Only if the skeleton does not already exist

    Publishes the application as a Tomcat context
    """
    require('web_root', 'tomcat_user', 'solr_home', 'catalina_home', provided_by=('staging', 'production'))
    if not files.exists(env.solr_home):
        run('mkdir %(solr_home)s' % env)
        run('mkdir -p %(solr_home)s/cores' % env)
        run('mkdir -p %(solr_home)s/data' % env)

        with cd(env.solr_home):
            # change permissions to solr_home dir and data
            sudo('chown %(tomcat_user)s data' % env)

            with lcd(os.path.join(env.local_project_root, 'solr')):
                # copy context.xml
                source = 'context_%(environment)s.xml' % env
                dest = 'context.xml'
                put(source, dest, mode=0644)

                # publishes the application described in context to Tomcat
                # by a symlink in Tomcat's context configuration dir
                ln_dest = '%(catalina_home)s/conf/Catalina/localhost/solr.xml' % env
                if files.exists(ln_dest):
                    sudo('rm %s' % ln_dest)
                sudo('ln -s %s/context.xml %s' % (env.solr_home, ln_dest))

        restart_tomcat()

@task
@roles('web')
def update_app():
    require('web_root', 'domain_root', 'local_project_root', 'tomcat_user',
            'solr_home', 'catalina_home', provided_by=('staging', 'production'))

    # check if cores definition solr.xml exists
    # ask to overwrite it or send warning
    puts_solr_xml = True
    if files.exists(os.path.join(env.solr_home, 'cores', 'solr.xml')):
        if not console.confirm('Are you sure you want to overwrite solr cores config file?',
                               default=False):
            puts_solr_xml = False
            utils.warn('Modify %(solr_home)s/cores/solr.xml file on server' % env)

    if puts_solr_xml:
        put(os.path.join(env.local_project_root, 'solr', 'solr.xml'),
            os.path.join(env.solr_home, 'cores', 'solr.xml'), mode=0644)



    # sync solr configuration files to remote
    # defaults rsync options: -pthrvz
    extra_opts = '--omit-dir-times'
    rsync_project(
        remote_dir = os.path.join(env.web_root, env.app_domain) ,
        local_dir = os.path.join(env.local_project_root, 'solr'),
        exclude=('.*', 'context_*.xml', 'solr.xml'),
        delete=True,
        extra_opts=extra_opts,
    )


    # symlink app in /home/www.openmunicipio.it/solr/ to /home/solr/cores/open_municipio
    ln_dest = '%(solr_home)s/cores/open_municipio' % env
    ln_src = '%(domain_root)s/solr' % env
    if files.exists(ln_dest):
        sudo('rm %s' % ln_dest)
    sudo('ln -s %s %s' % (ln_src, ln_dest))


    # create data dir if not existing
    with cd(os.path.join(env.solr_home, 'data')):
        if not files.exists('open_municipio'):
            sudo('mkdir -p open_municipio')
            sudo('chown tomcat55 open_municipio')

@roles('web')
@task
def rebuild_index():
    """
    rebuild solr index from scratch
    """
    require('settings', 'virtualenv_root', provided_by=('staging', 'production'))
    run_venv('django-admin.py rebuild_index --settings=%(settings)s' % env)

@roles('web')
@task
def update_index():
    """
    update solr index<<
    """
    require('settings', 'virtualenv_root', provided_by=('staging', 'production'))
    run_venv('django-admin.py update_index --settings=%(settings)s' % env)
