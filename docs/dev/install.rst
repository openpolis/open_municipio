.. -*- mode: rst -*-
 
========================================
Installing and configuring OpenMunicipio
========================================

.. contents::

Overview
========

This document is a step-by-step tutorial describing how to install and configure a working instance of *OpenMunicipio*
on a **local development environment**. Such a setup is intended for performing a test-drive of our web application, or
-- and this would be greatly appreciated ;-) -- for contributing back to the codebase.

Requirements
============
Since *OpenMunicipio* is built on top of the `Django`_ web development framework, first of all you need to make sure
that your OS environment satisfies the `corresponding requirements`_.

Following a widespread good practice in the Python community, we **strongly** encourage you to make use of the powerful
`virtualenv`_ tool, allowing the creation of isolated Python runtime environments.

An handy companion for virtualenv is `virtualenvwrapper`_, a set of scripts providing facilities to simplify the process
of creation and management of Python virtual environments.

Once installed a Python package manager (we strongly suggest `pip`_), you can install `virtualenv` and
`virtualenvwrapper` as follows:

.. sourcecode:: bash

 # pip install virtualenv virtualenvwrapper

On a Debian-like system, you may install pip via the OS package manager:

.. sourcecode:: bash

 # apt-get install python-pip

.. note::

   This command will result in a system wide installation of pip.  When using operating inside a virtualenv, though, the
   local version of pip will be used instead.  This point is important since the *system-wide* instance of pip will install Python
   packages so that they are available system-wide, while a *local* instance will install inside the corresponding
   virtualenv.

Moreover, the following software packages are required [#]_:

* ``python-dev`` (needed for compiling Python C-coded extension modules, such as `PIL`_ and `lxml`_)
* ``libxml2``, ``libxml2-dev``, ``libxslt1.1``, ``libxslt-dev``  (needed by lxml)
* ``mercurial``: needed for installing packages hosted on BitBucket


..  _Django: http://djangoproject.com/ 
.. _`corresponding requirements`: http://docs.djangoproject.com/en/dev/faq/install/
.. _`virtualenv`: http://pypi.python.org/pypi/virtualenv
.. _`virtualenvwrapper`: http://www.doughellmann.com/docs/virtualenvwrapper/
.. _`pip`: http://pip.readthedocs.org/
.. _`PIL`: http://www.pythonware.com/products/pil/
.. _`lxml`: http://lxml.de/


Tutorial
========

Configure virtualenwrapper
--------------------------

First of all, you need to configure virtualenwrapper.  

.. note::

   If you already have a working virtualenwrapper installation inside you home directory, you may skip this section.

Just add the following lines inside your ``.bashrc`` (or another script being loaded at shell startup-time):

.. code-block:: bash

   ## virtualenvwrapper configuration

   # root dir for the virtual environments managed by virtualenvwrapper
   export WORKON_HOME=$HOME/.virtualenvs

   ## pip-virtualenv(wrapper) integration

   # tell pip to use the same parent dir for virtual environments
   # as virtualenvwrapper
   export PIP_VIRTUALENV_BASE=$WORKON_HOME
   # tell pip to install distributions on the currently active virtualenv (if one) 
   export PIP_RESPECT_VIRTUALENV=true

   # initialize  virtualenvwrapper
   source /usr/local/bin/virtualenvwrapper.sh

In order for these changes to take effect, reload your ``.bashrc``:

.. code-block:: bash

   $ source ~/.bashrc

Now a handful of new shell commands -- provided by virtualenwrapper -- should be available to you.


Clone the source repository
---------------------------

You can get OpenMunicipio's source code by checking out the source repository on Github.  Assuming you want to check it
out under ``~/djcode/open_municipio``, just issue this command:

.. code-block:: bash                   

   git://github.com/openpolis/open_municipio.git

.. note::
   
   This way, you'll get a read-only version of the source repository -- i.e. you can modify the code but not pushing it
   back to GitHub; only OpenMunicipio developers are allowed to do that.  If you want to contribute, you may e.g. clone
   the repository and issue a pull-request.       
   
   
Create a new virtualenv
-----------------------

Now, create a new Python virtual environment for OpenMunicipio:

.. code-block:: bash
   
   $ mkvirtualenv --no-site-packages open_municipio

The name ``open_municipio`` is arbitrary, but make sure to pass the option ``--no-site-packages`` when creating the new
enviroment: this way, you are achieving a better "isolation" from the system-level Python installation.

Now, to activate the ``open_municipio`` virtual environment use:

.. code-block:: bash

   $ workon  open_municipio

while, to deactivate it, just type:

.. code-block:: bash

  (open_municipio)$ deactivate

Before continuing, take a few moment for configuring the new virtual environment.  Virtualenwrapper provides a few
"hooks", i.e. scripts which will be executed when virtualenwrapper-related events happen.  Particularly interesting to us are
``postactivate`` and ``postdeactivate``. So go to the virtualenv root directory
(i.e. ``~/.virtualenvs/open_municipio``), find ``postactivate`` and ``postdeactivate`` under ``bin``, and edit them as
follows:

.. code-block:: bash

   ## `~/.virtualenvs/open_municipio/bin/postactivate
   #!/bin/bash
   # This hook is run after this virtualenv is activated.
   PROJECT_ROOT=$HOME'/djcode/open_municipio'
   cd $PROJECT_ROOT
   export OLD_PYTHONPATH=$PYTHONPATH
   export PYTHONPATH=$PROJECT_ROOT:$PYTHONPATH
   export DJANGO_SETTINGS_MODULE='open_municipio.settings_local'


.. code-block:: bash

   ## `~/.virtualenvs/open_municipio/bin/postdeactivate
   #!/bin/bash
   # This hook is run after this virtualenv is deactivated.
   cd ~/
   export PYTHONPATH=$OLD_PYTHONPATH
   unset OLD_PYTHONPATH
   unset DJANGO_SETTINGS_MODULE

In order for these changes to take effect, just deactivate and re-activate you virtual environment. 


Install requirements
--------------------

In order to install OpenMunicipio's software dependencies, just issue this command -- after activating you virtual
environment:

.. code-block:: bash       

     (open_municipio)$ pip install -r requirements/main.txt

This tell pip to install every package listed within the file ``requirements/main.txt``, which list mandatory packages.
If you  also want to install optional packages (e.g. for building the documentation), issue this command:

.. code-block:: bash       

     (open_municipio)$ pip install -r requirements/extra.txt


Configure Django
----------------

A Django -- as OpenMunicipio -- reads its configuration from a so called *settings module*.  For convenience, we provide
*two* Django settings module

* ``open_municipio/settings.py`` is the top-level settings module, which contains generic settings, tweaked for the
  OpenMunicipio web platform. DO NOT edit this file !
* ``open_municipio/settings_local.py`` contains settings specific to a given OS environment.  It allows you to override
  the main settings module -- i.e. ``open_municipio/settings.py`` -- in order to suit your needs.

For easing OpenMunicipio setup, we provide an example instance of the "local" settings module, named
``settings_local.py.sample``.  In order to use it, just rename it to ``settings_local.py`` and edit it at your own
will. Consider, however, that it SHOULD work out-of-the-box.

Create the database
-------------------

Since we are operating in a local development environment, installing and configuring a full-fledged RDBMS (such as
PostgresSQL, MySQL, etc.) seems like overkill. A lightweight database engine such SQLite will be more than adequate.

So, to create the database/tables needed by OpenMunicipio, just issue this command:

.. code-block:: bash

        (open_municipio)$ django-admin.py syncdb 

When invoked, the ``sycndb`` Django command will prompt you for creating a superuser (needed e.g. for accessing the
administrative backend): you may either provide the requested information or skip this step and load that data using the
*test fixtures* we provide (see below for details).  In the latter case, you may want to use the ``--noinput`` flag:

.. code-block:: bash

        (open_municipio)$ django-admin.py syncdb --noinput

Load test data [optional]
-------------------------

For you convenience, we provide a set of test data (in the form of Django *fixtures*) to populate the database with a
bunch of fictitious -- but more-or-less realistic -- data.

In order to load these data, just issue this command:

.. code-block:: bash

        (open_municipio)$ django-admin.py loaddata test_data


Collect static files
--------------------

Static assets (e.g. images, CSS & Javascript files, etc.) must be collected in a single place, so the webserver is able
to serve them:

.. code-block:: bash

        (open_municipio)$ django-admin.py collectstatic


Install Solr
------------

OpenMunicipio relies on Solr for text indexing and searching; see `here </dev/solr_haystack>`_ for details. 

For a local development environment such this, there is no need to setup a complex installation: just use the servlet
engine bundled with the Solr distribution (called *Jetty*).  The complete details are `here </dev/solr_haystack>`_,
but for your convenience we'll do a brief recap.

#. download Solr distribution
#. generate the data schema and put it in place
#. start Jetty
#. build Solr index

Run the server
--------------

Finally, you should be ready to go: start the web server bundled with Django (a.k.a. *runserver* or *development
server*):

.. code-block:: bash

        (open_municipio)$ django-admin.py runserver

This command will start a (single-threaded) web server listening on port 8000 of the local loopback network interface.

.. note::

   We suggest you to issue this command in a dedicated shell window, so you can see the debugging output that the server
   prints to the console.


Celebrate !
-----------

Now, visit the URL http://localhost:8000 with a web browser: if all went well, you should see OpenMunicipio homepage.
    

Additional topics
=================

If you checkout a newer version of OpenMunicipio, you may need to do a little house-keeping in order to re-start the
development server. Shortly, every time you update OpenMunicipio code, you should perform these task, in order [#]_  :

#. update the database: Django use an ORM to represent database-level objects (tables, records, etc.) as native Python
   objects.  When the Django-level data model goes out-fo-sync with the database schema, you have to re-sync them. The
   quickiest and simplest way to perform this task **on development environments** is to drop and re-create the database
   from scratch. Taking into account the fact that a SQLite DB is just a single file, just follow these steps:

   * drop the old database        

    .. code-block:: bash

        (open_municipio)$ rm open_municipio/db.sqlite

   * re-create the database:

    .. code-block:: bash
       
           (open_municipio)$ django-admin.py syncdb [--noinput]

   * reload the test data:
 
    .. code-block:: bash

        (open_municipio)$ django-admin.py loaddata test_data

#. re-collect static assets:

   .. code-block:: bash

        (open_municipio)$ django-admin.py collectstatic

#. update Solr schema (see  `here </dev/solr_haystack>`_)

#. tell Solr to re-index documents (see  `here </dev/solr_haystack>`_)


Enabling the debug toolbar
--------------------------

Django features a handy third-party extension named `Django Debug Toolbar`_, providing a lot of useful debugging
facilities. To install it, just be sure to install the "extra" requirements and un-comment the following lines in
``settings_local.py``:

.. code-block:: python

    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('debug_toolbar.middleware.DebugToolbarMiddleware',)
    INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar',)


Building documentation
----------------------
OpenMunicipio uses `Sphinx`_ for maintaining its internal documentation.  To build the documentation:

* make sure to have installed Sphinx within you virtual environment (just install the "extra" requirements)    
* activate the virtualenv
* move to the ``docs`` directory of OpenMunicipio repository
* run the command:

  .. code-block:: bash  
  
        (open_municipio)$ make html

You'll find the docs (in HTML format) under the ``_build/html`` directory.

.. note::

   When the documentation is updated upstream (e.g. when you check out a new version of OpenMunicipio) you have to
   re-generate the documentation by running ``make html``


.. _`Django Debug Toolbar`: https://github.com/django-debug-toolbar/django-debug-toolbar
.. _`Sphinx`: http://sphinx.pocoo.org/


.. rubric:: Footnotes

.. [#] Note that, for the simplicity sake, we refer to the names these packages are available as on Ubuntu 10.04
       (i.e. our reference GNU/Linux distribution).  On other distros, those same packages may be available under
       alternative names.
.. [#] Even if they may not be all necessary, performing them is the recommended approach.
