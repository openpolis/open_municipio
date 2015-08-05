from fabric.api import cd, env, execute, hide, lcd, require, put, roles, run, settings, sudo, task
from fabric.utils import fastprint, warn
from fabric.contrib import files

import os

@task
def check_requirements():
    """
    Check if OS-level requirements are satisfied. 
    """
    raise NotImplementedError


def is_installed_package(pkg_name):
    """
    If package ``pkg_name`` has already been installed on the the target OS,    
    returns ``True``, ``False`` otherwise.
    """
    with hide('running', 'stdout', 'stderr'):
        result = run("dpkg-query -W -f='${Status}' %s" % pkg_name)
    if result == 'install ok installed':
        return True
    else:
        return False
        

def install_package(pkg_name):
    """
    Install a software package -- via APT -- on the target OS.
    
    Do nothing if the requested package is already installed 
    on the the target OS.
    
    Arguments:
    
    * ``pkg_name``: the name of the package to be installed.
    """
    with hide('commands'):
        if not is_installed_package(pkg_name):    
            sudo('apt-get install --yes %s' % pkg_name)


@task
@roles('admin')          
def install_system_requirements():
    """
    Install generic OS-level software required by OpenMunicipio. 
    """    
    fastprint("Installing generic software requirements...", show_prefix=True, end='\n')
    with hide('commands'):
        required_packages = ['mercurial',
                             'python-dev',
                             'libxml2', 
                             'libxml2-dev', 
                             'libxslt1.1', 
                             'libxslt-dev',
                             'postgresql-server-dev-8.4']
    for pkg_name in required_packages:
        fastprint("* %s" % pkg_name, end='\n')
        install_package(pkg_name)       

    # fix locales and LANG variable
    run('rm -f /etc/locale.gen')
    run('touch /etc/locale.gen && echo "%(locale)s UTF-8" >> /etc/locale.gen && /usr/sbin/locale-gen' % env)
    run('echo export LANG=%(locale)s >> /etc/profile' % env)

    run('update-locale LANG=%(locale)s' % env)

        
    
@task
@roles('admin')          
def create_system_user(username, home_dir=None, enable_passwd=False):
    """
    Create an OS-level user account.
    
    Arguments:
    
    * ``home_dir``: specify a home directory for the user (defaults to ``/home/<username>``)
    * ``enable_passwd``: specify if password-based logins are allowed or not (default to ``False``)   
    """
    fastprint("Creating user `%s'..." % username, show_prefix=True)
    with hide('commands', 'warnings'):
        with settings(warn_only=True):
            cmd = ['adduser']
            if home_dir is not None:
                cmd += ['--home %s' % home_dir]
            if not enable_passwd:
                cmd += ['--disabled-password']
            # set (empty) finger information, so no user input is required 
            cmd += ['--gecos', ',,,'] 
            cmd += [username]
            run(' '.join(cmd))      
    fastprint(" done." % env, end='\n')
        

@task
@roles('admin')          
def setup_web_user():
    """
    Create a passwordless account for ``WEB_USER`` on the remote machine(s).
    """
    require('web_user', 'web_root', 'web_user_hostkey', 
            provided_by=('staging', 'production'))
    with hide('commands'):
        # create system user
        create_system_user(env.web_user, home_dir=env.web_root)
        fastprint("Adding SSH key for user `%(web_user)s'..." % env, show_prefix=True)
        # copy SSH keyfile to a temporary remote location
        source = env.web_user_hostkey 
        tmpfile = '/tmp/id_rsa.pub'
        put(source, tmpfile, mode=0644)
        # create a ``.ssh/authorized_keys`` file, if not already existing
        run('mkdir -p %(web_root)s/.ssh' % env)
        auth_keys = os.path.join(env.web_root, '.ssh', 'authorized_keys') 
        run('touch %s' % auth_keys)
        # add the new key to the "authorized" ones
        run('cat %s >> %s' % (tmpfile, auth_keys))
        # adjust filesystem permissions
        run('chown -R %(web_user)s:%(web_user)s %(web_root)s' % env)
        fastprint(" done." % env, end='\n')
        

@task
@roles('admin')          
def setup_solr_user():
    """
    Create a passwordless account for ``solr`` user on the remote machine(s).
    """
    require('solr_home', 'solr_user_hostkey', provided_by=('staging', 'production'))
    with hide('commands'):
        # create ``solr`` user
        create_system_user('solr')
        fastprint("Adding SSH key for user `solr'...", show_prefix=True)
        # copy SSH keyfile to a temporary remote location
        source = env.solr_user_hostkey 
        tmpfile = '/tmp/id_rsa.pub'
        put(source, tmpfile, mode=0644)
        # create a ``.ssh/authorized_keys`` file, if not already existing
        run('mkdir -p %(solr_home)s/.ssh' % env)
        auth_keys = os.path.join(env.solr_home, '.ssh', 'authorized_keys') 
        run('touch %s' % auth_keys)
        # add the new key to the "authorized" ones
        run('cat %s >> %s' % (tmpfile, auth_keys))
        # adjust filesystem permissions
        run('chown -R solr:solr %(solr_home)s' % env)
        fastprint(" done." % env, end='\n')


@task
@roles('admin')          
def setup_instance_user():
    """
    Create a passwordless account for ``OM_USER`` on the remote machine(s).
    """
    require('om_user', 'domain_root', 'om_user_hostkey', 
           provided_by=('staging', 'production'))
    with hide('commands'):
        # create system user
        create_system_user(env.om_user, home_dir=env.domain_root)
        fastprint("Adding SSH key for user `%(om_user)s'..." % env, show_prefix=True)
        # ensure that ``OM_USER``'s home directory actually exists
        # needed if ``create_system_user()`` fails (e.g. because ``OM_USER`` already exists)
        run('mkdir -p %(domain_root)s' % env)
        # copy SSH keyfile to a temporary remote location
        source = env.om_user_hostkey 
        tmpfile = '/tmp/id_rsa.pub'
        put(source, tmpfile, mode=0644)
        with cd(env.domain_root):
            # create a ``.ssh/authorized_keys`` file, if not already existing
            run('mkdir -p .ssh' % env)
            auth_keys = os.path.join('.ssh', 'authorized_keys') 
            run('touch %s' % auth_keys)
            # add the new key to the "authorized" ones
            run('cat %s >> %s' % (tmpfile, auth_keys))
        # adjust filesystem permissions
        run('chown -R %(om_user)s:%(om_user)s %(domain_root)s' % env)
        fastprint(" done." % env, end='\n')


@task
@roles('solr')    
def setup_tomcat():  
    """
    Perform Tomcat-related provisioning tasks on the target OS.
    """
    with hide('stdout'):
        fastprint("Installing Tomcat...", show_prefix=True)
        # install DEB package for Tomcat v6
        install_package('tomcat6')
        fastprint(" done." % env, end='\n')
        fastprint("Addding `tomcat' user to group `www-data'...", show_prefix=True)
        # add the Tomcat user to the webserver group (``www-data``, for a Debian-like OS)
        sudo('adduser %(tomcat_user)s www-data' % env)
        fastprint(" done." % env, end='\n')


@task
@roles('solr')    
def update_solr_context():
    """
    Upload ``context.xml`` to the remote server(s),
    choosing the proper local version -- i.e. ``context_(staging|production).xml``.
    """
    require('environment', 'local_repo_root', 'solr_home', 
            provided_by=('staging', 'production'))
    fastprint("Uploading Solr context file...", show_prefix=True)
    with hide('commands'):
        source = os.path.join(env.local_repo_root, 'solr', 'context_%(environment)s.xml' % env)
        dest = os.path.join(env.solr_home, 'context.xml')
        put(source, dest, mode=0644)
    fastprint(" done." % env, end='\n')
    
    
@task
@roles('solr')    
def setup_solr():
    """
    Perform Solr-related provisioning tasks on the target OS.
    """
    require('solr_download_link', 'solr_install_dir', 'solr_home', 
            'tomcat_user', 'local_repo_root', 'catalina_home',
            provided_by=('staging', 'production'))
    with hide('commands'):
        setup_tomcat()
        # add Tomcat's user to the ``solr`` group
        fastprint("Addding `tomcat' user to group `solr'...", show_prefix=True)
        sudo('adduser %(tomcat_user)s solr' % env)
        fastprint(" done." % env, end='\n')
    # sanity check
    if files.exists(env.solr_home):
        warn("Directory %(solr_home)s already exists" % env)         
    ## Sorl installation procedure
    with hide('commands'): 
        with cd('/tmp'):      
            # download Solr distribution
            fastprint("Downloading Solr distribution...", show_prefix=True)
            run('wget %(solr_download_link)s' % env)
            fastprint(" done." % env, end='\n')
            fastprint("Unpacking Solr distribution...", show_prefix=True)
            tarball =  env.solr_download_link.split('/')[-1]
            dist_dir = os.path.splitext(tarball)[0]
            # extract compressed archive containing Solr distribution 
            run('tar xzvf %s' % tarball)
            fastprint(" done." % env, end='\n')
            ## copy Solr distribution in place
            fastprint("Installing Solr...", show_prefix=True)
            if files.exists(os.path.join('/home', dist_dir)):
                if dist_dir.startswith('apache-solr'): # safety check
                    sudo('rm -rf %s' % os.path.join('/home', dist_dir))
            sudo('mv %(dist_dir)s /home/' % {'dist_dir': dist_dir})
            # adjust permissions
            sudo('chown -R solr:solr %(solr_install_dir)s' % env)
            fastprint(" done." % env, end='\n')
            # cleanup
            fastprint("Cleaning up...", show_prefix=True)
            run('rm -f %s' % tarball)
            fastprint(" done." % env, end='\n')
        ## initial setup for Solr
        with cd(env.solr_home):
            # create general filesystem layout
            fastprint("Creating `solr/cores' dir...", show_prefix=True)
            run('mkdir -p cores')
            fastprint(" done." % env, end='\n')
            fastprint("Creating `solr/data' dir...", show_prefix=True)
            run('mkdir -p data')
            # Solr data dir must be writable by Tomcat
            sudo('chmod 2770 %s' % os.path.join(env.solr_home, 'data'))
            fastprint(" done." % env, end='\n')
            # upload a context file (needed by Tomcat)
            with lcd(os.path.join(env.local_repo_root, 'solr')):
                    execute(update_solr_context)
                    fastprint("Publishing Solr context to Tomcat...", show_prefix=True)
                    # publish application described in ``context.xml`` to Tomcat
                    # by dropping a symlink under Tomcat's context configuration dir
                    ln_src = os.path.join(env.solr_home, 'context.xml')
                    ln_dest = os.path.join(env.catalina_home, 'localhost', 'solr.xml')
                    with settings(warn_only=True):
                        sudo('rm -f %s' % ln_dest)
                    sudo('ln -s %s %s' % (ln_src, ln_dest))
                    fastprint(" done." % env, end='\n')
                    fastprint("Uploading skeleton configuration file for cores...", show_prefix=True)
                    # upload a skeleton file for Solr cores' configuration
                    src = 'solr.xml'
                    dest = os.path.join('cores', 'solr.xml')  
                    put(src, dest, mode=0644)
                    fastprint(" done." % env, end='\n')
        # Tomcat must be restarted in order for the changes to take effect                
        restart_tomcat()

@task
@roles('solr')
def restart_tomcat():
    """
    Restart Tomcat servlet engine.
    """    
    require('tomcat_controller', provided_by=('staging', 'production'))
    fastprint("Restarting Tomcat...", show_prefix=True)
    with hide('commands'):
        sudo('%(tomcat_controller)s restart' % env)
    fastprint(" done." % env, end='\n')


@task
@roles('web')        
def setup_postgres():
    """
    Perform PostgreSQL-related provisioning tasks on the target OS.
    """
    require('local_repo_root', 'postgres_conf_dir',  
            provided_by=('staging', 'production'))
    # install DEB package for PostgreSQL 
    install_package('postgresql')
    # upload conf files
    with hide('commands'):       
        with lcd(os.path.join(env.local_repo_root, 'postgres')):
            with cd(os.path.join(env.postgres_conf_dir)):
                fastprint("Updating `postgresql.conf'...", show_prefix=True)
                put('postgresql.conf', 'postgresql.conf' , mode=0644, use_sudo=True)
                sudo('chown postgres:postgres %(postgres_conf_dir)s/postgresql.conf' % env)
                fastprint(" done." % env, end='\n')
                fastprint("Updating `pg_hba.conf'...", show_prefix=True)
                put('pg_hba.conf', 'pg_hba.conf', use_sudo=True)
                sudo('chmod 0640 %(postgres_conf_dir)s/pg_hba.conf' % env)
                sudo('chown postgres:postgres %(postgres_conf_dir)s/pg_hba.conf' % env)
                fastprint(" done." % env, end='\n')
    execute(restart_postgres)
    
    
@task
@roles('admin')
def restart_postgres():
    """
    Restart PostgreSQL database server.
    """
    require('postgres_controller', provided_by=('staging', 'production'))
    fastprint("Restarting Postgres...", show_prefix=True)
    with hide('commands'):
        sudo('%(postgres_controller)s restart' % env)
    fastprint(" done." % env, end='\n')
