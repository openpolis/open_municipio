from fabric.api import *

from fabfile.venv import run_venv

import os

## Static files management
@task
def collect_files():
    require('static_root','virtualenv_root', provided_by=('staging', 'production'))
    # safety checks
    assert env.static_root.strip() != '' and env.static_root.strip() != '/'
    # Before Django 1.4 we don't have the ``--clear`` option to ``collectstatic``
    run('rm -rf %(static_root)s/*' % env)
    run_venv('django-admin.py collectstatic -v 0 --noinput --settings=%(settings)s' % env)
