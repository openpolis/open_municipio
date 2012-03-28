.. -*- mode: rst -*-

=================
Solr and Haystack
=================
*OpenMunicipio* relies on Solr_ for content indexing, textual search and faceted navigation
in some of its main sections.


Solr installation
-----------------
Solr is a search server built using the Lucene_ Java library. It must be installed within a `servlet container`_.

Java 1.6 is needed in order to use the latest version of Solr (3.5, as of this writing).

It's beyond the scope of this documentation to show how to install and configure properly an external
servlet container in a production environment.

Solr comes with a self-contained servlet container (Jetty_), which can be safely used
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
To access Solr services within Django, both for write and read access (indexing and querying), you use Haystack_,
which features a unified API allowing you to plug in different search backends (Solr, Xapian, Woosh).

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
  $ django-admin.py rebuild_index

where ``SOLR_DOWNLOAD`` is the directory where you have downloaded and unpacked the Solr package.

The first step is needed only if you want to save Solr's default schema file.


.. _haystack: http://haystacksearch.org/

