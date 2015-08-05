## -*- mode: python -*-
"""
Fabric script (a.k.a. "fabfile") to automate the deployment process 
of an instance of the OpenMunicipio web application.

Deployment on both staging & production machine(s) is supported:

* To deploy on the staging server(s), run the shell command ``fab staging deploy``
* To deploy on the production server(s), run the shell command ``fab production deploy``

The first time you perform a deploy on a given machine (or set of machines), you MUST
use the command  `fab (staging|production) initial_deploy`` instead, which takes care
of performing one-time initialization tasks.

In order to customize the deployment procedure to suit your specific needs, 
you can control the behaviour of this script by setting up the provided configuration files
(``conf_staging.py`` and ``conf_production.py`` for staging and production deployment,
respectively).   
"""
from fabric.utils import abort
from fabric.api import cd, env, execute, hide, lcd, put, require, roles, run, settings, sudo, task

import code, database as db, venv, static, webserver, solr, provision

import os


## Environment-specific setup
@task
def staging():
    """
    Deploy OpenMunicipio to the staging server(s).
    """
    # import staging's conf module
    import conf_staging as conf
    ## set up Fabric global environment dictionary
    env.environment = 'staging'
    env.server = conf.SERVER_MACHINE    
    env.project = conf.PROJECT_NAME
    env.locale = conf.LOCALE
    env.app_domain = conf.APP_DOMAIN
    env.local_repo_root = conf.LOCAL_REPO_ROOT
    env.local_project_root = conf.LOCAL_PROJECT_ROOT
    env.rsync_exclude = conf.RSYNC_EXCLUDE
    env.python = conf.PYTHON_FULL_PATH   
    env.web_user = conf.WEB_USER
    env.web_user_hostkey = conf.WEB_USER_HOSTKEY
    env.om_user = conf.OM_USER
    env.om_user_hostkey = conf.OM_USER_HOSTKEY
    env.web_root = conf.WEB_ROOT
    env.domain_root = conf.DOMAIN_ROOT
    env.virtualenv_root = conf.VIRTUALENV_ROOT
    env.project_root = conf.PROJECT_ROOT
    env.settings = conf.DJANGO_SETTINGS_MODULE
    env.static_root = conf.STATIC_ROOT
    # Tomcat
    env.tomcat_user = conf.TOMCAT_USER
    env.tomcat_controller = conf.TOMCAT_CONTROLLER
    env.catalina_home = conf.CATALINA_HOME
    # Solr
    env.solr_user_hostkey = conf.SOLR_USER_HOSTKEY
    env.solr_download_link = conf.SOLR_DOWNLOAD_LINK
    env.solr_install_dir = conf.SOLR_INSTALL_DIR
    env.solr_home = conf.SOLR_HOME
    # PostgreSQL
    env.postgres_conf_dir = conf.POSTGRES_CONF_DIR
    env.postgres_controller = conf.POSTGRES_CONTROLLER
    env.db_user = conf.DB_USER 
    env.db_name = conf.DB_NAME
    # role definitions
    env.roledefs = {                   
    'admin': ['root@%(server)s' % env],
    'web': ['%(web_user)s@%(server)s' % env],
    'db': ['root@%(server)s' % env],
    'solr': ['solr@%(server)s' % env],
    'om': ['%(om_user)s@%(server)s' % env],
    }
 
@task
def production():
    """
    Deploy OpenMunicipio to the production server(s).
    """
    env.environment = 'production'
    abort('Production deployment not yet implemented.')


## Macro-tasks

@task
def setup_platform():
    """
    Take care of all preliminay tasks needed to setup the OS of the 
    target machine(s) in order for the deploy of an OpenMunicipio instance
    to be possible.
    """
    with hide('commands'):
        require('environment', provided_by=('staging', 'production'))
        # install generic  software requirements:
        execute(provision.install_system_requirements)
        # setup a passwordless account for ``WEB_USER``
        execute(provision.setup_web_user)
        # setup a passwordless account for ``solr`` user
        execute(provision.setup_solr_user)
        # setup Solr (include Tomcat's setup)
        execute(provision.setup_solr)
        # setup PostgreSQL
        execute(provision.setup_postgres)

    
@task
def initial_deploy():
    """
    Deploy the web application to remote server(s) **for the first time**.

    The first deployment procedure may differ from subsequent ones,
    since some initialization tasks have to be performed only once.

    Some examples:
    * fake South migrations
    * ..
    """
    require('environment', provided_by=('staging', 'production'))
    with hide('commands'):
        env.initial_deploy = True
        execute(deploy)        


@task
@roles('om')
def deploy():
    """
    Deploy the web application to remote server(s)
    """
    require('environment', 'local_repo_root', 'domain_root',
            provided_by=('staging', 'production'))
    with hide('commands'):       
        ## one-time initialization steps go here  
        if env.get('initial_deploy'):
            # setup a passwordless account for ``OM_USER``
            execute(provision.setup_instance_user)
            # create the initial filesystem layout
            execute(code.make_website_skeleton)
            # upload helper scripts
            # TODO: HACK ! Consider using virtualenwrapper, instead.
            with lcd(env.local_repo_root):
                with cd(os.path.join(env.domain_root, 'private')):
                    src = 'load_venv_%(environment)s.sh' % env
                    dest = 'load_venv.sh'
                    put(src, dest, mode=0644)
            # add a new core for this OpenMunicipio instance
            execute(solr.add_new_core)
            # drop any existing application DB
            execute(db.drop_db)
            # create a new database user -- who will own the application DB 
            execute(db.create_user)
        ## tasks to be performed each time the application is deployed on the server
        # sanity check
        with hide('everything'):
            if run('test -d %(domain_root)s' % env).failed:
                abort("It seems that the root dir for this OpenMunicipio instance has not been created, yet.") 
        with settings(warn_only=True):
            execute(webserver.stop)
        # update Django project's files
        execute(code.update_project)
        # update external dependencies
        execute(venv.update_requirements)
        if env.get('initial_deploy'):
            # execute ``syncdb`` Django task
            execute(db.sync_db)
        # apply DB migrations (if any)
        execute(db.migrate)
        # update Solr context
        execute(provision.update_solr_context)
        # update Solr core's conf
        execute(solr.update_core_conf)
        # update Solr index
        execute(solr.update_index)
        # collect static files
        execute(static.collect_files)
        # clear webserver's log when deploying to the staging server
        if env.environment == 'staging': execute(webserver.clear_logs)
        # update webserver configuration
        execute(webserver.update_conf)
        execute(webserver.start)
        # adjust filesystem permissions
        execute(adjust_permissions)


@roles('om') 
def adjust_permissions():
    """
    Adjust filesystem permissions after completing the deployment process.
    """
    pass
