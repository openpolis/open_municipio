from fabric.api import *
from fabric.contrib import files
from fabric.context_managers import cd, lcd, settings

import os


## Virtual environment management
@task
def create():
    """Create a virtualenv on remote host"""
    require('virtualenv_root', provided_by=('staging', 'production'))
    from fabfile import PYTHON_FULL_PATH
    args = '--clear --python=%s --no-site-packages' % PYTHON_FULL_PATH
    run('virtualenv %s %s' % (args, env.virtualenv_root))


def ensure_virtualenv():
    """Check if a project-specific virtualenv already exists; if not, create it."""
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
    context manager)
    """
    require('virtualenv_root', provided_by=('staging', 'production'))
    env.activation_script = os.path.join(env.virtualenv_root, 'bin/activate')
    cmd = ['source %(activation_script)s' % env]
    cmd += ['export PYTHONPATH=%(project_root)s:$PYTHONPATH' % env ] # configure PYTHONPATH
    cmd += [command] # shell command to be run within this virtualenv
    run(' && '.join(cmd), **kwargs)


@task
def update_requirements():
    """
    Update external dependencies on remote host.
    """
    require('project_root', provided_by=('staging', 'production'))
    ensure_virtualenv()
    requirements_dir = os.path.join(env.project_root, 'requirements')
    # TODO: generalize to multiple requirement files
    with cd(requirements_dir):
        pip_executable = os.path.join(env.virtualenv_root, 'bin', 'pip')              
        cmd = [pip_executable] # use pip version provided by virtualenv              
        cmd += ['install']
        cmd += ['--upgrade'] # upgrade already installed packages
        cmd += ['--requirement %s' % os.path.join(requirements_dir, 'main.txt')] # specify a requirement file
        run(' '.join(cmd))
