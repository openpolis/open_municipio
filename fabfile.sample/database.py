from fabric.api import *
from fabric.contrib import files, console
from fabric.context_managers import cd

from venv import run_venv

## Database management
@task
def create():
    """
    Create the application's database on the server machine.
    """
    raise NotImplementedError

@task
def drop():
    """
    Delete the application's database on the server machine.
    """
    require('code_root', provided_by=('staging', 'production'))
    with cd(env.code_root):
        if files.exists('sqlite.db'):
            run('rm -f sqlite.db')

@task
def sync_remote():
    """
    Sync the application's database on the server machine.
    """
    require('settings', 'virtualenv_root', provided_by=('staging', 'production'))
    run_venv('django-admin.py syncdb --noinput --settings=%(settings)s' % env)
    
@task
@roles('web')
def update():
    """
    Update remote database (including South migrations, if any).
    """
    require('settings','code_root', provided_by=('staging', 'production'))
    drop()
    run_venv('django-admin.py syncdb --all --noinput --settings=%(settings)s' % env)
    with cd(env.code_root):
        if files.exists('sqlite.db'):
            sudo('chgrp www-data sqlite.db')
            sudo('chmod g+w sqlite.db')
    # if getattr(env, 'initial_deploy', False):
    #     run_venv('django-admin.py syncdb --all --noinput --settings=%(settings)s' % env)
    #     run_venv('django-admin.py migrate --fake --noinput --settings=%(settings)s' % env)
    # else:
    #     run_venv('django-admin.py syncdb --all --noinput --settings=%(settings)s' % env)
    #     run_venv('django-admin.py migrate --noinput --settings=%(settings)s' % env)
