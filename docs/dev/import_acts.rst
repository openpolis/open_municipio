Importing acts into open_municipio
==================================

The following chapter describes how to import one or more acts into the open_municipio dataset.

Acts are provided as XML files, (schema: OM-XML.xsd) within a workflow described in `data_import`.

Architecture
------------

The import is performed by launching a django management task on the *instance*, through a fab task.
The task is defined by extending the generic
`open_municipio.import_data.commands.ImportActsCommand`, in the *core* open_municipio module.

**core**
::

    open_municipio.data_import
     |- management
     |  |- commands
     |     |- sample_import_acts.py - Command(open_municipio.commands.ImportActsCommand)
     |
     |- commands
        |- ImportActsCommand

**instance**
::

     open_udine.data_import
     |- management
        |- commands
           |- udine_import_acts.py - Command(open_municipio.commands.ImportActsCommand)


This architecture provides flexibility in adapting the import code to different situations likely arising in
the instances. It is sufficient to override the methods in the ImportActsCommand.


Usage
-----
Test import while developing (core)::

    django-admin.py sample_import_acts ~/Workspace/om_data/deliberation_sample.xml --act-type=CouncilDeliberation --dry-run


Import acts in remote (instance)::

    fab staging tasks.import_acts:/home/open_municipio/udine.staging.openmunicipio.it/data/inbox/acts/20120622_ATTI_2008/deliberation_*,act_type=CouncilDeliberation


Notes
-----
The XML file is passed as arguments using absolute path and *globbing* can be used so that the script process
more than one file (i.e. `/home/om-udine/data/acts/deliberation_*.xml`)

The task needs a mapping between external and internal people IDs. This file can be specified using the `--people-file`
options on the command line, but a default consistent value is set in the configurations
(`conf.py` and `settings.py` of the instance).

This is an xml file that contains the sequence of mapping between Person instances.
::

    <om:Person id="HOFU" om_id="1" first_name="Furio" last_name="Honsell"/>

The `conf.py` file is used to specify some of the import parameters.
It is used both for acts and votations import.

Importing acts is an *idempotent* operation, that is it can be performed more than once, without changing
the results beyond the first import. Thanks to this, it is possible to refresh the news of the imported acts,
selectively (using the `--refresh-news` option). News related to the acts are removed,
the import is performed and without actually duplicating the acts, the news are ri-generated.
Care has been taken in order to properly generate all related news.

