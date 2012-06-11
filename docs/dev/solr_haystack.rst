.. -*- mode: rst -*-

==============================
Content indexing and searching
==============================

Overview
========

The *OpenMunicipio* web application relies on Solr_, a powerful search server, for content indexing, textual search and
faceted navigation in some of its main sections.

This document aims at detailing the steps required to deploy Solr (and the related technology stack) on:

* a local development environment
* remote staging/production machines


.. _Solr: http://lucene.apache.org/solr/

Architecture
============

Solr is a wrapper around Apache's `Lucene`_ Java library, providing core text-indexing and searching capabilities.  Solr
adds to Lucene -- among many other things -- an HTTP, REST-like interface which can be used by clients both for indexing
documents (via POST requests carrying e.g. XML payloads) and for querying the search index (via GET requests returning
data in XML, JSON or a few other formats).  This way, the application server (e.g. Apache + mod_wsgi) and the search
server run as independent processes, talking via the HTTP protocol; a little schema may be of help here::

    web clients   --->  web server (e.g Apache)  <--->  application server (e.g mod_wsgi)  <----->  Solr

As we said, the search server can receive instructions to add or remove documents from the index, via POST requests.
This may be done through a variety of methods, according to the chosen **update policy**:

 * **real-time**: the web application directly updates the index whenever a change is detected;
 * **batch**: for example, via a Django management command;
 * **message queues**: a setup generally required only for advanced and complex integrations.

.. warning::

    For security reasons it's strongly advised not to expose the Solr search server on the Internet.  Web application(s)
    -- in this case, OpenMunicipio -- may connect to it by establishing a TCP connection on the local loopback interface
    (if they both run on the same machine) or by a TCP connection over a private network (in case their processes reside
    on different machines).    

Solr also provides a web UI for carrying out administrative tasks and submitting direct queries to the server (useful
e.g. for testing purposes).

The Solr search server is implemented as a `Java servlet`_, so it must be executed inside a Java `servlet container`_.
Every servlet container implementation conforming to the `J2EE`_ specification (e.g. `Tomcat`_, `Jboss`_, `Jetty`_, ...)
will do.

Finally, we need an abstraction layer to access Solr services from Django, both for write and read access (indexing and
querying).  Currently, the de-facto standard in this domain is `Haystack`_, a Django application providing for search
systems what the Django ORM provides for RDBMS: a a unified Python API allowing you to plug in different search backends
(Solr, `Xapian`_, `Woosh`_).


.. _`Lucene`: http://lucene.apache.org/
.. _`Java servlet`: http://en.wikipedia.org/wiki/Servlet
.. _`servlet container`: http://en.wikipedia.org/wiki/Web_container
.. _`J2EE`: http://en.wikipedia.org/wiki/J2EE
.. _`Tomcat`: http://tomcat.apache.org/
.. _`Jboss`: http://www.jboss.org/
.. _`Jetty`: http://jetty.codehaus.org/jetty/
.. _`Haystack`: http://haystacksearch.org/
.. _`Xapian`: http://xapian.org/
.. _`Woosh`: https://bitbucket.org/mchaput/whoosh/wiki/Home


Development environment
=======================

Setting up Solr for a local development environment is quite simple, just follow these steps:

#. install Jetty & Solr
#. install Haystack
#. add Haystack-related configuration to the ``open_municipio/settings_local.py`` module
#. generate the data schema and put it in place
#. build Solr index


Jetty
-----

When setting up a local development environment, installing and configuring a full-fledged servlet container (such as
Tomcat) is likely to be overkill.  In fact, the Solr software distribution bundles a lightweight servlet container,
named `Jetty`_.

.. warning::

   It is strongly recommended not to use this setup in production environments !

In order to setup Jetty, just:

#. `download`_ the latest stable release of Solr, as a compressed ``.tgz`` or ``.zip`` archive
#. extract that archive within your home directory, e.g ``$SOLR_HOME=~/tmp/apache-solr-X.Y.Z``
#. run the Jetty executable: 
   
   .. code-block:: bash 
      
    $ cd $SOLR_HOME/example && java -jar start.jar

#. Thats it! Now Jetty should be up and running.  Make sure to execute this command within a separate terminal window
   (so you can watch for console output) and not to close that window while you are running OpenMunicipio (otherwise,
   some URLs -- notably the "list" pages -- can't load correctly).            

.. note::

   In order to stop a running instance of the Jetty server, just hit ``Ctrl+D`` when the corresponding terminal window
   is active.


The new Solr instance is running on port 8983 (by default), and its home directory is ``$SOLR_HOME/example/solr``.
Of course, these values may be modified, tweaking the configuration, but this will not be covered here.

After starting Solr, visit its admin interface: http://localhost:8983/solr/admin. It's just a quick check that everything is working properly.

There are no data yet, since no indexing process was launched: see the `Building Solr's content index`_ section below.


.. _`Jetty`: http://jetty.codehaus.org/jetty/
.. _`download`: http://lucene.apache.org/solr/mirrors-solr-latest-redir.html


Solr
----

You have already "installed" Solr by extracting the compressed archive in ``$SOLR_HOME``; no further configuration steps
are required.

.. note::
   
   Java 1.6 or later is needed in order to use the latest version of Solr (3.6, as of this writing).


Haystack
--------

Installation
~~~~~~~~~~~~
Using Haystack with Solr requires you to install, separately, the ``pysolr`` and ``lxml`` Python packages.

The ``requirements/main.txt`` pip requirements file contains directives for installing the stable release of Haystack, with its
required dependencies, so all you need to do is to keep your virtualenv up-to-date.

Configuration
~~~~~~~~~~~~~

Haystack can be configured following these simple steps:

#. add ``haystack`` to ``INSTALLED_APPS`` in ``settings.py``
#. add the following Haystack-related settings to your ``settings_local.py`` module:

   .. sourcecode:: python

      # haystack configuration parameters
      HAYSTACK_SITECONF = 'open_municipio.search_sites'
      HAYSTACK_SEARCH_ENGINE = 'solr'
      HAYSTACK_SOLR_URL = 'http://127.0.0.1:8983/solr'
      HAYSTACK_SEARCH_RESULTS_PER_PAGE = 10

Usage notes
~~~~~~~~~~~

Building Solr's data schema
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before you can start indexing contents stored within the OpenMunicipio database, you have to tell Solr what are the
contents you wish to index and how they are structured.  This task is accomplished by crafting a suitable XML document,
called the **data schema**, which must be saved in a file named ``schema.xml``.

Luckily, Haystack allows you to abstract away this step: instead of hand-writing this XML file, you can use a
Python-based declarative syntax (similar to that used for defining Django model classes).  Just place these declarations
into Python modules named ``search_indexes.py`` within your Django apps: Haystack will automagically discover them and build the
data schema for you!

.. note::

   As usual, only those apps listed by ``INSTALLED_APPS`` are taken into account by Haystack when auto-discovering
   ``search_indexes.py`` modules.

To generate the data schema for Solr, just use the ``build_solr_schema`` Django management command (added by
``django-haystack``).  This script will output the schema definition on the console's standard ouptut; then, you need to
copy this output to the proper location in order for Solr to find it.  Assuming that ``$SOLR_HOME`` is the filesystem
location where you extracted the archive containg Solr's distribution, just proceed as follows:

.. code-block:: bash

     $ mv $SOLR_HOME/example/solr/conf/schema.xml $SOLR_DOWNLOAD/example/solr/conf/schema.xml.orig
     $ django-admin.py build_solr_schema > $SOLR_HOME/example/solr/conf/schema.xml

The first step is optional and is needed only if you want to save Solr's default schema file.

After updating the data schema, restart Jetty in order for the change to take effect.

.. note::

   You have to repeat this process every time the database schema changes (or, at least, when that portion of the
   database schema relevant to the indexing process changes).

       

Building Solr's content index
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now, you can start indexing content from the database: just use the ``rebuild_index`` Django management command (added by
``django-haystack``):

.. sourcecode:: bash

  $ django-admin.py rebuild_index


That's it !

.. note::

   Depending on your chosen update policy, you may need to re-run this command every time new content is added to (or
   removed from) the database.

 

Staging & Production setups
===========================

Deploying Solr on server machines for production use is somewhat different than setting it up on local machines for
internal use (e.g. testing, development, etc.).  Here, we outline the setup we would recommend for a Solr installation
serving multiple OpenMunicipio's instances at a time (a setup a.k.a. **multicore**). 

For the simplicity sake, we assume that both the Solr server and the web application server are running on the same
server machine. If you need to split Solr and the web server on different machines (e.g. for high-traffic websites),
the single steps might differ, but the overall process should be quite similar to that described below.                

Tomcat
------

Installation
~~~~~~~~~~~~

First of all, we need a servlet container for running Solr.  Our choice for a production setup is `Tomcat`_, but every
servlet container implementation conforming to the `J2EE`_ specification should do.

.. note::

   This deploy process has been tested against Tomcat 6; other Tomcat versions should work with minor or no modifications at all,
   but your mileage may vary.

It's beyond the scope of this documentation to show how to install and configure properly an external
servlet container in a production environment; just for reference, on a Debian-like GNU/Linux system, the following
command will install Tomcat 6:

.. code-block:: bash

   # apt-get install tomcat6

As a pre-requisite for what follows, the Tomcat application server must be up and running; we refer you to the `official
Tomcat documentation`_ for further details.

Lets define the ``$CATALINA_HOME`` variable as the home directory for the Tomcat server. For a Debian-like system, its
``/usr/share/tomcat6``.


Configuration
~~~~~~~~~~~~~

Solr
----

As we said, our deployment scenario consists of a single Solr server instance serving multiple OpenMunicipio's instances
at a time. When Solr is configured to run in this `operation mode`_ (called **multicore**), each client application (in our
case, an instance of OpenMunicipio) is allocated a separated **core**, an application-specific data structure comprising:

* a dedicated *search index*
* a dedicated set of configuration files

This way, each application is allowed to build (and, subsequently, query) its own search index; moreover, Solr behaviour
can be configured on a per-application basis.


..  _`operation mode`: http://wiki.apache.org/solr/CoreAdmin

Installation
~~~~~~~~~~~~

Solr installation is performed as we said before for development setups: just download the compressed archive containing
the Solr distribution and extract it under a suitable filesystem location (e.g. ``/home/apache-solr-3.6.0``). Make sure this
directory tree is readable by the user the Tomcat process run as (``tomcat``, on a Debian-like system).

Initial configuration
~~~~~~~~~~~~~~~~~~~~~

First of all, we need to perform a few server-level configuration tasks; then, we can start adding cores to the Solr server.

#. Create a root directory for holding Solr-related data and configuration files.  A good choice may be e.g.  ``/home/solr``.
   Henceforth, we refer to this directory as ``$SOLR_HOME``.  It may be convenient to create a dedicated system user (say
   ``solr``) owning this directory:

   .. code-block:: bash  

      # adduser --disabled-password solr

   Note the console logins have been disabled for this user for security reasons: run ``su - solr`` instead (as superuser).

#. Under ``$SOLR_HOME``, create ``data`` and ``cores`` directories:  

   * the ``data`` dir will hold search indexes for the various cores; Tomcat needs write access to this directory, so adjust
     permission accordingly;
   * the ``cores`` dir will contain application-specific cores

#. Create a ``context.xml`` file, under ``$SOLR_HOME``. This file defines Tomcat's context (execution environment) for
   Solr, including:

   * the location of the ``.war`` (*w*\eb *ar*\chive) file packaging the Solr webapp
   * the environment variable ``solr/home`` setting the filesystem path to the root directory containing cores'
     configuration (in this case, ``/home/solr/cores``)
   
   A sample ``context.xml`` may be as follow:
   

   .. sourcecode:: xml

     <?xml version="1.0" encoding="utf-8"?>
     <Context docBase="/home/apache-solr-3.6.0/dist/apache-solr-3.6.0.warhome/solr/solr.war" debug="0" crossContext="true">
         <Environment name="solr/home" type="java.lang.String" value="/home/solr/cores" override="true"/>
     </Context>

#.  Create the following symlink:

    .. code-block:: bash 
    
        ln -s $SOLR_HOME/context.xml /etc/tomcat6/conf/Catalina/localhost/solr.xml

#. Restart Tomcat:

   .. code-block:: bash 

     # /etc/init.d/tomcat6 restart


.. _`Tomcat`: http://tomcat.apache.org/
.. _`official Tomcat documentation`: http://tomcat.apache.org/tomcat-6-doc/index.html

This procedure is implemented in the ``fabfile.sample/solr.py`` module, which can be used to automate the deploy
process.



Adding a new core
~~~~~~~~~~~~~~~~~

Solr configuration for a multicore setup is contained into the file ``$SOLR_HOME/cores/solr.xml``.  In order to add a
new core to the existing set of cores, you have to edit this file.  Follow these steps:

#. An existing ``solr.xml`` file may look as follow (assuming we have already defined 2 cores):

   .. code-block:: xml

        <?xml version="1.0" encoding="UTF-8" ?>
        <solr persistent="false" sharedLib="lib">
            <cores adminPath="/admin/cores" shareSchema="true">
                <core name="XXX.openmunicipio.it" instanceDir="XXX.openmunicipio.it" dataDir="${solr.data.dir:../../data}/XXX.openmunicipio.it" />
                <core name="YYY.openmunicipio.it" instanceDir="YYY.openmunicipio.it" dataDir="${solr.data.dir:../../data}/YYY.openmunicipio.it" />
             </cores>
        </solr>

   To add a new core, just add a ``<core>`` element as a child of the ``<cores>`` element:

   .. code-block:: xml

      <core name="ZZZ.openmunicipio.it" instanceDir="ZZZ.openmunicipio.it" dataDir="${solr.data.dir:../../data}/ZZZ.openmunicipio.it"/>

   where the ``name`` attribute is a label for the core and the ``instanceDir`` attribute is the the configuration directory
   for this core (under ``$SOLR_HOME/cores``).
      
#. Add a core-specific configuration directory under ``$SOLR_HOME/cores``. An example configuration directory may be
   found under ``solr.sample`` in the OpenMunicipio distribution.  Alternatively, you may substitute
   ``$SOLR_HOME/cores/ZZZ.openmunicipio.it`` with a symlink to the application-specific ``solr`` directory on the remote
   server (e.g. ``/home/open_municipio/ZZZ.openmunicipio.it/private/solr``):

   .. code-block:: bash 

       ln -s /home/open_municipio/ZZZ.openmunicipio.it/private/solr /home/solr/cores/ZZZ.openmunicipio.it 


   That's the technique we've used in our deploy script.

#. Create the directory ``/home/solr/data/ZZZ.openmunicipio.it``.  Tomcat needs write access to it, so make sure that
   filesystem permissions are properly set.

#. Edit the The ``solrconfig.xml`` file in ``ZZZ.openmunicipio.it/cores/conf``, so that the ``dataDir`` element looks this way:

   .. sourcecode:: xml

      <dataDir>${solr.data.dir:/home/solr/data/ZZZ.openmunicipio.it}</dataDir>

#. Restart Tomcat.

Now Solr should be up and running, and accessible at the URL ``http://hostname:8080/solr``. There, you should see a link
similar to *Admin ZZZ.openmunicipio.it*, pointing to ``http://hostname:8080/solr/admin/ZZZ.openmunicipio.it``.  At this
point you may even query the search index, but no results would be returned -- since no content has been indexed, yet.


Modifying core-specific configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A core may need to be re-configured for various reasons:

* the data schema (``/home/XXX.openmunicipio.it/solr/conf/schema.xml``) has to be regenerated since the database schema
  changed;
* we need to apply more advanced changes, for example to the ``solrconfig.xml`` and other core-specific files
  (``stopwords``, ``protwords``, ``synonyms``).

In each of these cases, after updating the configuration directory for the core, Tomcat must be restart in order for the
changes to take effect.

Haystack
--------

Installation
~~~~~~~~~~~~

Refer to the corresponding section above.

Configuration
~~~~~~~~~~~~~

Refer to the corresponding section above.

Content indexing
================

Querying Solr index
===================




