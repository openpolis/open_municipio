.. -*- mode: rst -*-

=================
Solr and Haystack
=================
*OpenMunicipio* relies on Solr_, a search server, for content indexing, textual search and faceted navigation
in some of its main sections.

Architecture
------------
The web server (apache) and the search server (solr) live as two different resources and communicate through the
http protocol.

.. waring::

For security reasons it is adviced not to expose the Solr server as a public resource.
It must be reachable from the eweb application, internally on in a private network.

The web application can query the search server through GET requests, receiving XML or Json responses ::

    User   --->  Apache (port 80)  <--->  WSGI  <----->  Solr (port 8180)

The search server can also receive instructions to add or remove documents from the index, through POST requests.
This is usually done through a variety of methods, according to the update policy:

 * real-time, the web application directly updates the index when a change is detected
 * batch commands, for example a python maangement command
 * queue and messages, for advanced and complex integrations

To access Solr services within Django, both for write and read access (indexing and querying), you use Haystack_,
which features a unified API allowing you to plug in different search backends (Solr, Xapian, Woosh).

Solr installation
-----------------
Solr is a search server built using the Lucene_ Java library. It must be installed within a `servlet container`_.

Java 1.6 is needed in order to use the latest version of Solr (3.5, as of this writing).

It's beyond the scope of this documentation to show how to install and configure properly an external
servlet container in a production environment.

Solr comes with an embedded servlet container (Jetty_), which can be safely used
for testing and development purposes.

.. warning::

   It is strongly recommended not to use this setup in production environments.


To install Solr, download_ it as a compressed file and unpack it into your local filesystem.
To start Solr, cd into the ``example`` directory and invoke the ``start.jar`` command:

.. sourcecode:: bash

  $ cd apache-solr-X.X.X/example
  $ java -jar start.jar

Now Solr is running on port 8983 (by default), and its ``home`` directory is ``solr/``, under ``example/``.
These values may be modified, tweaking the configuration, but this will not be covered here.

After starting Solr, visit its admin interface: http://localhost:8983/solr/admin.
It's just a quick check that everything is working properly.

There are no data, since no indexing process was launched. Proceed to the configuration section.


.. _Solr: http://lucene.apache.org/solr/
.. _download: http://lucene.apache.org/solr/mirrors-solr-latest-redir.html
.. _Lucene: http://lucene.apache.org/
.. _`servlet container`: http://en.wikipedia.org/wiki/Web_container
.. _Jetty: http://jetty.codehaus.org/jetty/


Haystack installation
---------------------
Using Haystack with Solr requires you to install, separately, ``pysolr`` and ``lxml``.
The ``requirements/main.txt`` ``pip`` requirements file contains instruction for installing the stable release of Haystack, with its
required dependencies, so all you need to do is to keep up your virtualenv up-to-date.


Haystack configuration
----------------------
Haystack can be configured following these simple steps:

1. add ``haystack`` to ``INSTALLED_APPS`` in `settings.py`
2. add the following haystack-related settings to your ``settings_local.py`` module:

.. sourcecode:: python

  # haystack configuration parameters
  HAYSTACK_SITECONF = 'open_municipio.search_sites'
  HAYSTACK_SEARCH_ENGINE = 'solr'
  HAYSTACK_SOLR_URL = 'http://127.0.0.1:8983/solr'
  HAYSTACK_SEARCH_RESULTS_PER_PAGE = 10

Haystack usage
--------------
Once haystack configuration is ok, you can start using it!

Haystack reads automatically the definitions of which of your model's classes to index and how,
from ``search_indexes.py`` files within your apps.

Now, first you need to build -- or re-build -- the ``schema.xml`` file, that is used by Solr to read the structure
of the documents it has to index.

Secondly, you need to pass the data from your database, in order for Solr to index them.

This can be done with **two** django management commands (added by ``django-haystack``):

.. sourcecode:: bash

  $ mv $SOLR_DOWNLOAD/example/solr/conf/schema.xml $SOLR_DOWNLOAD/example/solr/conf/schema.xml.000
  $ django-admin.py build_solr_schema > $SOLR_DOWNLOAD/example/solr/conf/schema.xml
  restart the embedded Jetty server, by using CTRL+C and ``java -jar start.jar``
  $ django-admin.py rebuild_index

where ``SOLR_DOWNLOAD`` is the directory where you have downloaded and unpacked the Solr package.

The first step is needed only if you want to save Solr's default schema file.


.. _haystack: http://haystacksearch.org/


Deploy (tomcat)
---------------
To deploy Solr in production or staging, the following instructions are valid for Tomcat_ v. 5.5.
For later versions, there should be no problems, but your mileage may vary.

Instructions are condensed in the Fabric_ ``fabfile.sample/solr.py``, used to automate the deploy process.

As a pre-requisite, the Tomcat application server must be up and running.
How to do this is out of the scope of the current document and `documentation regarding Tomcat`_
can be found on the official website.

``CATALINA_HOME`` is the root directory of the Tomcat server. For a Debian distribution,
when installed with ``apt-get install tomcat55``, this is ``/usr/share/tomcat55``.

1. Create directory for solr configurations and data (ex: ``/home/solr``).
   Hencefort ``SOLR_HOME``. See the tree below.

2. Change permissions so that tomcat user can write into ``$SOLR_HOME/data``.

3. Create a ``context.xml`` file, under ``$SOLR_HOME``. This defines the Tomcat Context for solr.

4. Symlink ``$SOLR_HOME/context.xml`` into ``$CATALINA_HOME/conf/Catalina/localhost/solr.xml``.

5. Restart tomcat.

6. Put solr.xml, containing the configuration for multicore solr indexes, into ``$SOLR_HOME/cores``.

7. Sync ``$SOLR_HOME/cores/open_municipio`` with a valid configuration from the local machine
(see ``solr.sample`` folder in our distribution).

Alternatively, you may substitute ``$SOLR_HOME/cores/open_municipio`` with a symlink to
the application specific folder on the remote server (where your web site and code, reside).

That's the technique we've used in our ``fabfile.sample/solr.py`` script.


This is the tree structure under  ``$SOLR_HOME``::

    /home/solr
      solr.war
      context.xml
      cores
        solr.xml
        open_municipio
          conf
            solrconfig.xml
            schema.xml
            ...
      data


This is the content of ``context.xml``

.. sourcecode:: xml

  <?xml version="1.0" encoding="utf-8"?>
  <Context docBase="/home/solr/solr.war" debug="0" crossContext="true">
    <Environment name="solr/home" type="java.lang.String" value="/home/solr/cores" override="true"/>
  </Context>

This is the content of ``cores/solr.xml``

.. sourcecode:: xml

  <?xml version="1.0" encoding="UTF-8" ?>

  <solr persistent="false" sharedLib="lib">

    <cores adminPath="/admin/cores" shareSchema="true">
      <core name="open_municipio" instanceDir="open_municipio" dataDir="${solr.data.dir:" />
    </cores>
  </solr>

The ``solrconfig.xml`` file in ``cores/open_municipio/conf``, must be edited,
changing the content of the ``dataDir`` element, to look this way:

.. sourcecode:: xml

  <dataDir>${solr.data.dir:/home/solr/data/open_municipio}</dataDir>



These are the Fabric commands to use, to deploy solr into a staging server,
having ``tomcat`` up and running:

.. sourcecode:: bash

  $ fab staging solr.make_common_skeleton
  $ fab staging solr.update_app
  $ fab staging solr.rebuild_index

.. _Tomcat: http://tomcat.apache.org/
.. _`documentation regarding Tomcat`: http://tomcat.apache.org/tomcat-5.5-doc/index.html
.. _Fabric: http://docs.fabfile.org/en/1.4.0/index.html