.. -*- mode: rst -*-

=================
Solr and Haystack
=================
*Openmunicipio* relies on Solr_ for content indexing, textual search and faceted navigation
in some of its main sections.


Solr installation
-----------------
Solr is a search server built using the Lucene_ java library, it must be installed within a `servlet container`_.

Java 1.6 is needed in order to use Solr latest version (3.5), as of this writing.

It's beyond the scope of this documentation to show how to install and configure properly an external
servlet container in a production environment.

Solr comes with a self contained servlet container (Jetty_), which can be safely used
for testing and development purposes.

.. note::

   It is strongly recommended not to use this setup in production's environments.


To install Solr, download_ it as a compressed file and decompress it into one of your directories.
To start Solr, cd into the example directory and invoke the ``start.jar`` command:

.. sourcecode:: bash

    > cd apache-solr-X.X.X/example
    > java -jar start.jar

Now Solr is running on port 8983 (default port), and its ``home`` directory is ``example/solr/``.
This values may be modified, tweaking the configuration, but this will not be covered here.

To visit Solr's admin interface: http://localhost:8983/solr/admin.
It's just to check that everything is working properly.

There are no data, since no indexing process was launched. Proceed to the configuration section.


.. _Solr: http://lucene.apache.org/solr/
.. _download: http://lucene.apache.org/solr/mirrors-solr-latest-redir.html
.. _Lucene: http://lucene.apache.org/
.. _`servlet container`: http://en.wikipedia.org/wiki/Web_container
.. _Jetty: http://jetty.codehaus.org/jetty/


Haystack installation
---------------------
To access solr services within django, both for writing and reading access (indexing and querying), you use Haystack_,
which features a unified API that allows you to plug to different search backends (Solr, Xapian, Woosh).

Using Haystack with Solr requires you to install, separately, ``pysolr`` and ``lxml``.
The ``requirements/main.txt`` contains instructions to install the stable release of Haystack, with its
required dependencies, so all you need is to keep up with your packages upgrades.


Haystack configuration
----------------------
Haystack may be simply configured, by these steps:

1. add ``haystack`` to the list of your applications in ``settings.py``
2. add the following haystack-related settings to your ``settings_local.py``:

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
in ``search_indexes.py`` files within your apps.

Now, first you need to build, or re-build the ``schema.xml`` file, that is used by Solr to read the structure
of the documents it has to index.
Second, you need to pass the data from your database, in order for Solr to index them.

This can be done with **two** django management tasks (added by ``django-haystack``):

.. sourcecode:: bash

  > mv $SOLR_DOWNLOAD/example/solr/conf/schema.xml $SOLR_DOWNLOAD/example/solr/conf/schema.xml.000
  > django-admin.py build_solr_schema > $SOLR_DOWNLOAD/example/solr/conf/schema.xml
  > django-admin.py rebuild_index

``SOLR_DOWNLOAD`` is the directory where you have downloaded and decompressed the Solr ``.tgz`` package.

The first step is needed only if you want to save Solr's default schema file.


.. _haystack: http://haystacksearch.org/


Production deploy (tomcat)
--------------------------
To deploy Solr in production, the following instructions are valid for Tomcat_ v. 5.5.
For later versions, there should be no problems, but your mileage may vary.

As a pre-requisite, the Tomcat application server must be up and running.
How to do this is out of the scope of the current document and `documentation regarding Tomcat`_
can be found on the official website.

``CATALINA_HOME`` is the root directory of the Tomcat server. For a Debian distribution,
when installed with ``apt-get install tomcat55``, this is ``/usr/share/tomcat55``.

1. Create directory for solr configurations and data (ex: /home/solr).
   Hencefort ``SOLR_HOME``. See the tree below.

2. Change permissions so that tomcat user can write into data.

3. Copy the ``solr.war`` file into ``$SOLR_HOME``.

4. Create a ``context.xml`` file, under ``$SOLR_HOME``. This defines the Tomcat Context for solr.

5. Symlink ``$SOLR_HOME/context.xml`` into ``$CATALINA_HOME/conf/Catalina/localhost/solr.xml``.

6. Start tomcat.


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
      <core name="open_municipio" instanceDir="open_municipio" dataDir="${solr.data.dir:../../data}/open_municipio" />
    </cores>
  </solr>

The ``solrconfig.xml`` file in ``cores/open_municipio/conf``, must be edited,
changing the content of the ``dataDir`` element, to look this way:

.. sourcecode:: xml

  <dataDir>${solr.data.dir:/home/solr/data/open_municipio}</dataDir>



.. _Tomcat: http://tomcat.apache.org/
.. _`documentation regarding Tomcat`: http://tomcat.apache.org/tomcat-5.5-doc/index.html
