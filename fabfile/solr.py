from fabric.api import cd, env, execute, get, hide, local, put, require, roles, sudo, task
from fabric.contrib.project import rsync_project
from fabric.contrib import files
from fabric.utils import fastprint

from venv import run_venv
from provision import restart_tomcat

from lxml import objectify
import os


## Solr management

@task
@roles('om')
def update_core_conf():
    """
    Update Solr core's configuration files on the remote machine(s), 
    syncing them with local ones.
    """
    require('domain_root', 'app_domain', 'local_repo_root',  
            provided_by=('staging', 'production'))   
    # update configuration -- on the remote machine -- for the Solr core  
    # serving this OpenMunicipio instance (via rsync)
    # defaults rsync options: -pthrvz
    fastprint("Syncing Solr configuration for %(app_domain)s..." % env, show_prefix=True)
    extra_opts = '--omit-dir-times'
    with hide('commands'):
        rsync_project(
            remote_dir=os.path.join(env.domain_root, 'private'),
            local_dir=os.path.join(env.local_repo_root, 'solr'),
            exclude=('.*', '*~','context_*.xml', 'solr.xml', 'solr.xml.remote'),
            delete=True,
            extra_opts=extra_opts,
        )
        sudo('chown -R om:www-data %s' % os.path.join(env.domain_root, 'private', 'solr'))
    fastprint(" done." % env, end='\n')

    
@task
@roles('solr')
def add_new_core():
    """
    Add a Solr core for the current OpenMunicipio instance.
    """
    require('domain_root', 'app_domain', 'local_repo_root', 'solr_home', 
            provided_by=('staging', 'production'))
    execute(update_core_conf)
    ## symlink configuration dir for the new core
    with hide('commands', 'warnings'):
        ln_dest = '%(solr_home)s/cores/%(app_domain)s' % env
        ln_src = os.path.join(env.domain_root, 'private', 'solr')
        if files.exists(ln_dest, use_sudo=True):
            fastprint("Removing file %s..." % ln_dest, show_prefix=True)
            sudo('rm -f %s' % ln_dest)
            fastprint(" done." % env, end='\n')
        fastprint("Symlinking core configuration...", show_prefix=True)    
        sudo('ln -s %s %s' % (ln_src, ln_dest))
        fastprint(" done." % env, end='\n')
        ## create a data dir for this core, if not existing
        with cd(os.path.join(env.solr_home, 'data')):
            if not files.exists(env.app_domain):
                fastprint("Creating a data dir for this core...", show_prefix=True)
                sudo('mkdir -p %(app_domain)s' % env)
                # Tomcat needs write permissions to cores' data dirs
                sudo('chmod 2770 %(app_domain)s' % env) 
                fastprint(" done." % env, end='\n')
        ## add to ``solr.xml`` a definition for the new core (as an additional ``<core>`` element)  
        with cd(env.solr_home):
            # copy remote version of ``solr.xml`` to the local machine
            fastprint("Adding new core definition to `solr.xml'... ", show_prefix=True)
            tmp_fname = os.path.join(env.local_repo_root, 'solr', 'solr.xml.remote')
            get(remote_path=os.path.join('cores', 'solr.xml'), local_path=tmp_fname)
            # parse ``solr.xml`` into a tree of Python objects
            tree = objectify.parse(tmp_fname)
            # retrieve the ``<cores>`` XML element
            cores_el = tree.getroot().cores
            # build a factory function for ``<core>`` elements
            E = objectify.ElementMaker(annotate=False)
            CORE = E.core
            # if a core definition for this OpenMunicipio instance already exists, 
            # drop it.
            existing_cores = [el.attrib['name'] for el in cores_el.iterchildren()]
            if 'om-udine' in existing_cores:
                [cores_el.remove(el) for el in cores_el.iterchildren() if el.attrib['name'] == 'om-udine']
            # append a new ``<core>`` element to ``<cores>``
            cores_el.append(CORE(name='om-udine',  
                                 instanceDir=env.app_domain,
                                 dataDir='%(solr_home)s/data/%(app_domain)s' % env
                                 ))
            # write back to ``solr.xml.remote``
            tree.write(tmp_fname, pretty_print=True, xml_declaration=True, encoding='UTF-8')
            # update ``solr.xml`` on the server machine
            src = tmp_fname
            dest = os.path.join('cores', 'solr.xml')  
            put(src, dest, mode=0644)
            # cleanup
            local('rm %s' % tmp_fname)
            fastprint(" done." % env, end='\n')
            restart_tomcat()

@task
@roles('om')
def update_data_schema():
    """
    Update Solr data schema.
    """
    require('settings', 'domain_root', 'web_user', 
            provided_by=('staging', 'production'))
    with hide('commands'):
        fastprint("Updating Solr data schema... ", show_prefix=True)
        run_venv('django-admin.py  build_solr_schema--settings=%(settings)s > %(domain_root)s/private/solr/conf/schema.xml' % env)
        sudo('chmod -R %(web_user)s:www-data %(domain_root)s/private/solr')
        execute(restart_tomcat)
        fastprint(" done." % env, end='\n')

@task
@roles('om')
def rebuild_index():
    """
    Rebuild Solr index from scratch.
    """
    require('settings', provided_by=('staging', 'production'))
    with hide('commands'):
        fastprint("Rebuilding Solr index... ", show_prefix=True)
        run_venv('django-admin.py rebuild_index --settings=%(settings)s' % env)
        fastprint(" done." % env, end='\n')
        
@task
@roles('om')
def update_index():
    """
    Update Solr index.
    """
    require('settings', 'virtualenv_root', provided_by=('staging', 'production'))
    with hide('stdout', 'running'):
        fastprint("Updating Solr index... ", show_prefix=True)
        run_venv('django-admin.py update_index --settings=%(settings)s' % env)
        fastprint(" done." % env, end='\n')