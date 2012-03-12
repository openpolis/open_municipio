.. -*- mode: rst -*-
 
=======================
Making database queries
=======================

.. contents::

Overview
========
 
This document describes the facilities provided by *OpenMunicipio* for executing some common database queries; think of
them as a sort of internal, private API, built on top of Django's database API and providing an higher-level,
domain-specific abstraction layer.  

This way, a significant portion of data-access logic can be encapsulated within Django's model layer, leading to more
concise, readable and maintainable views and templates.

.. warning::

   Note that this API is meant for internal use only, and may be subject to frequent changes.


Institutions, charges & groups
==============================

Since the portion of DB schema describing people-related entities (institutions, gropus, charges, etc.) and their
relationships is quite involved, extracting relevant pieces of information from the database is not a straightforward
task. So, we have designed and implemented a convenience API providing quick and easy access to those objects most
commonly needed when writing views and templates.

The API is currently implemented as a sort of DOM tree, embedding the hierarchy of objects which comprise a municipality (at least from a
logical standpoint).  This object tree may be navigated by accessing the ``municipality``, which is the root object of
the tree and acts as an entry point to the underlying hierarchy.  

In order to use the API, just import the root object:

.. sourcecode:: python

   from open_municipio.people.models import municipality

The  ``municipality`` object hierarchy currently provides access to the following items:

Mayor
-----

* ``municipality.mayor.as_institution``:  the municipality mayor, as an ``Institution`` instance
* ``municipality.mayor.as_charge``:  the municipality mayor, as an ``InstitutionCharge`` instance

Council
-------

* ``municipality.council.as_charge``:  the city council, as an ``Institution`` instance

* ``municipality.council.members``: members of the city council (aka *counselors*), as a QuerySet of ``InstitutionCharge``
  instances

* ``municipality.council.majority_members``:  majority counselors, as a ``Set`` of  ``InstitutionCharge`` instances

* ``municipality.council.minority_members``:  minority counselors, as a ``Set`` of ``InstitutionCharge`` instances

* ``municipality.council.groups``:  groups of counselors within the city council, as a QuerySet of ``Group`` instances

* ``municipality.council.majority_groups``:  counselors' groups belonging to majority, as a QuerySet of ``Group`` instances

* ``municipality.council.minority_groups``:  counselors' groups belonging to minority, as a QuerySet of ``Group`` instances
 

City Government
---------------

* ``municipality.gov.members``: members of the city government (aka *assessors*), as a QuerySet of ``InstitutionCharge`` instances


.. note::

   Notice that all the objects returned by this API are **current**, i.e. they describe a municipality as observed at
   the current time. Past records (e.g. expired charges, old groups' composition, etc.) are automatically filtered out.







