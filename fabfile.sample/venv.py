from fabric.api import env, hide, put, require, roles, run, settings, task
from fabric.utils import fastprint
from fabric.contrib import files

import os


## Virtual environment management
@task
@roles('om')
def create():
    """
    Create a virtualenv on remote host.
    """
    fastprint("Creating a new virtualenv..." % env, show_prefix=True)
    with hide('commands'):
        require('virtualenv_root', provided_by=('staging', 'production'))
        args = '--clear --python=%s --no-site-packages' % env.python
        run('virtualenv %s %s' % (args, env.virtualenv_root))
    fastprint(" done." % env, end='\n')


def ensure_virtualenv():
    """
    Check if a project-specific virtualenv already exists; if not, create it.
    """
    require('virtualenv_root', provided_by=('staging', 'production'))
    if files.exists(os.path.join(env.virtualenv_root, 'bin', 'python')):
        return
    else:
        create()


def virtualenv(venv_root):
    """
    This context manager is intended for specifying a virtualenv to use.
    
    Note that it should be used only for selecting a virtualenv different from
    the project-specific one (available from ``env.virtualenv_root``)
    """
    return settings(virtualenv_root=venv_root)


def run_venv(command, **kwargs):
    """
    Run a command (via ``fabric.api.run``) within a given virtualenv context 
    (to be specified either via ``env.virtualenv_root`` or the ``virtualenv`` 
    context manager).
    """
    require('virtualenv_root', 'domain_root', provided_by=('staging', 'production'))
    env.activation_script = os.path.join(env.virtualenv_root, 'bin/activate')
    cmd = ['source %(activation_script)s' % env]
    cmd += ['export PYTHONPATH=%s:$PYTHONPATH' % os.path.join(env.domain_root, 'private')] # configure PYTHONPATH
    cmd += [command] # shell command to be run within this virtualenv
    run(' && '.join(cmd), **kwargs)


@task
@roles('om')
def update_requirements():
    """
    Update external dependencies on remote host.
    """
    require('virtualenv_root', 'domain_root', 'local_repo_root', 
            provided_by=('staging', 'production'))
    ensure_virtualenv()
    fastprint("Updating OpenMunicipio dependencies..." % env, show_prefix=True)
    with hide('commands'):
        # upload pip requirements file to the server
        source = os.path.join(env.local_repo_root, 'requirements.txt')
        requirement_file = dest = os.path.join(env.domain_root, 'private', 'requirements.txt')
        put(source, dest, mode=0644)
        pip_executable = os.path.join(env.virtualenv_root, 'bin', 'pip')              
        cmd = [pip_executable] # use pip version provided by virtualenv              
        cmd += ['install']
        # TODO: verify that --upgrade removes files in the src directory
        cmd += ['--upgrade'] # upgrade already installed packages
        cmd += ['--requirement %s' %  requirement_file] # specify a requirement file
        run(' '.join(cmd))
    fastprint(" done." % env, end='\n')