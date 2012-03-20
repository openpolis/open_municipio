Generating random test data
===========================

Introduction
------------
The scripts inside this directory allows a developer to create *startup random items* to 
test the software, before the import procedure is implemented.

This may be useful in the development phase, or for unit or functional testing purposes.

Prerequisites
-------------
These python packages must be installed in the environment

* lorem-ipsum-generator
* -e git://github.com/openpolis/rst2pdf-patched-docutils-0.8#egg=rst2pdf
 
The last package is a patched version of the rst2pdf package, that takes into account the issues introduced by 
docutils > 0.8 as described in issue #25.

The database must not contain valuable records, since the scripts start by cleaning up some tables.
Using an empty test database and environment may be the best approach.
These are the cleanup instructions as of the time of this writing, and they may vary in the future:

.. sourcecode:: python 

    Person.objects.all().delete()
    InstitutionCharge.objects.all().delete()
    Institution.objects.all().delete()
    Group.objects.all().delete()
    Act.objects.all().delete()
    Sitting.objects.all().delete()
    Votation.objects.all().delete()

Launching the scripts
---------------------
Scripts must be launched inside the project environment (if you're not using virtualenvs, then, go fetch it)
It is advised to use the following order:

.. sourcecode:: python 

    python open_municipio/testdatabuilder/create_startup_people.py
    python open_municipio/testdatabuilder/create_startup_acts.py
    python open_municipio/testdatabuilder/create_startup_votes.py

What the scripts mean
---------------------

create_startup_people
+++++++++++++++++++++
Simulates a whole *Comune*, as to the Institutions (Mayor, City government, Council, Commissions and Council Groups).
Names and other anagraphical data are taken randomly from Openpolis.it database and mixed, to form new, unknown persons.
Commissions and groups are defined in the script's source code.

At the end of this script you'll have the Persons and InstitutionCharges for all the Institution (and Commissions), 
and the Groups will be popolated as well.

create_startup_acts
+++++++++++++++++++
Simulates creation of a number of acts. Acts types and number are specified currently in the script's source code.

Deliberations get a title, a text, a random number of first-signer (1-3), co-signers (0-5) and pdf attachments (0-5).
PDF's are generated randomly with lorem-ipsum content and uploaded into the uploads directory, according to django specification.

create_startup_votes
++++++++++++++++++++
A council *Sitting* containing a number of *Votations* is generated.

Each Votation has ChargeVotes added for each member. The percentages of YES, NO, ABST and ABSENT are computed using
weighted probabilities. Probabilities are defined in the source code, currently.

Votes are **not linked** to acts. They could be linked, of course, but are left linkless, to map
the current situation in the datasets coming from the municipalities we're dealing with.


Creating a taxonomy
-------------------
In order to create a taxonomy -- i.e. a classification based on categories and tags -- for existing acts, just launch this command from a terminal:

.. sourcecode:: bash

   $ python open_municipio/testdatabuilder

There are a few parameters you may customize to tweak the way the taxonomy is generated (the configuration file is ``testdatabuilder/conf.py``):

* ``MIN_CATEGORIES_PER_ACT``: min number of categories associated with an act (default: ``0``)
* ``MAX_CATEGORIES_PER_ACT``: max number of categories associated with an act (default: ``3``)
* ``MIN_TAGS_PER_CATEGORY``: given an act, min number of tags associated with each category (default: ``0``)
* ``MAX_TAGS_PER_CATEGORY``: given an act, max number of tags associated with each category (default: ``5``)


Todos
-----

* Add other acts types (motion, interrogation, city government acts ...)
* Votings weight probabilities expressed by couselors vary according to group and majority
* Definitions (groups, commissions,probability weights, ...) are moved from the source code to a configuration file
* Integrate with testing framework for testing purposes
* Implement signals to generate news after new acts or votes are created.


