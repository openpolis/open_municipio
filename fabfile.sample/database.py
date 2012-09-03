from fabric.api import env, hide, require, roles, run, settings, task 
from fabric.utils import abort, fastprint, puts
from fabric.contrib import console

from venv import run_venv



## Database management
@task
@roles('db')
def create_user():
    """
    Create a database user for accessing the application's database.
    """
    require('db_user', provided_by=('staging', 'production'))
    fastprint("Creating PostgreSQL user `%(db_user)s'..." % env, show_prefix=True)
    with hide('commands', 'warnings'):
        with settings(warn_only=True):
            run('createuser E --no-superuser --no-createrole --createdb %(db_user)s' % env)
    fastprint(" done." % env, end='\n')


@task
@roles('db')
def drop_db():
    """
    Destroy the application's database on the server machine.
    """
    # TODO: add a confirmation prompt
    require('db_name', provided_by=('staging', 'production'))
    fastprint("Dropping database `%(db_name)s'...   " % env, show_prefix=True)
    if not console.confirm("Are you sure?"):
        abort("Deployment aborted.")
    with hide('commands', 'warnings'):
        with settings(warn_only=True):
            run('dropdb %(db_name)s' % env)
    fastprint("Dropped database %(db_name)s." % env, end='\n')
    
@task
@roles('om')
def sync_db():
    """
    Syncronize the application's database on the server machine.
    """
    require('settings', provided_by=('staging', 'production'))
    fastprint("Running `syncdb'...", show_prefix=True)
    with hide('commands'):
        run_venv('django-admin.py syncdb --noinput --settings=%(settings)s' % env)
    fastprint(" done." % env, end='\n')
    

@task
@roles('om')
def migrate():
    """
    Apply migrations (if any) on the application's database on the server machine.
    """
    pass