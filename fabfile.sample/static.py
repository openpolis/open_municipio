from fabric.api import env, hide, require, roles, run, task
from fabric.utils import fastprint

from venv import run_venv

## Static files management
@task
@roles('om')
def collect_files():
    """
    Collect static files on the remote machine.
    """
    require('static_root','virtualenv_root', provided_by=('staging', 'production'))
    fastprint("Collecting static files..." % env, show_prefix=True)
    with hide('commands'):
        # safety checks
        assert env.static_root.strip() != '' and env.static_root.strip() != '/'
        # Before Django 1.4 we don't have the ``--clear`` option to ``collectstatic``
        run('rm -rf %(static_root)s/*' % env)
        run_venv('django-admin.py collectstatic -v 0 --noinput --settings=%(settings)s' % env)
    fastprint(" done." % env, end='\n')