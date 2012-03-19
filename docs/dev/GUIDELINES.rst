.. -*- mode: rst -*-
 
=========================
Guidelines for developers
=========================

.. contents::

Generalities
============

This document collects guidelines to be followed by developers willing to contribute to **OpenMunicipio**.

Please be sure to adhere to these coding standards when writing code intended to be included within
**OpenMunicipio**\ 's codebase.

Unless otherwise stated, you MUST follow `PEP 8`_ (aka *Style Guide for Python Code*) and `Django Coding Style`_
guidelines.

In case of conflicts, assume this order of precedence:

* this document
* `Django Coding Style`_ guidelines
* `PEP 8`_ 


.. _`PEP 8`: https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/
.. _`Django Coding Style`: https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/


Language
--------

For the sake of consistency, these pieces of text MUST be written in **English**:

* source code 
* source code's comments 
* documentation intended for developers
* commit messages (for the version control system used by the project -- currently, Git)
* development-related issues (a.k.a. tickets),  including comments made to them

These pieces of text, instead, MUST be written in **Italian**:

* documentation intended for end-users


Indentation
-----------

* Source code MUST be indented by 4 spaces (**NO tabs**, please !). 

  * for `vim` users, these options should do the trick:

    .. sourcecode:: vim

        set expandtab
        set tabstop=4
        set shiftwidth=4
    
Comments
--------

* documentation included within source code files, including docstrings, comments, etc. SHOULD be formatted following
  ``docutils`` conventions (i.e. using the `reStructuredText`_ markup syntax)

.. _`reStructuredText`: http://docutils.sourceforge.net/rst.html


Python module's import order
----------------------------

Python modules should be imported at the top of source files for readability
reasons (non-module-level imports -- if needed -- are an exception, of course!).

Module-level imports SHOULD follow this order:

* modules included with the official Django distribution
* modules provided by 3-rd party Django apps
* project-specific modules
* system libraries

Settings
--------

Values of Django settings MUST be accessed via the proxy object ``django.conf.settings``, NOT by importing the
``settings.py`` module.

That is to say, in order to access e.g. ``STATIC_ROOT`` use:
  
.. code-block:: python

   from django.conf import settings
   value = settings.STATIC_ROOT

DON'T use:

.. code-block:: python

   import mysite.settings
   value = settings.STATIC_ROOT


Naming conventions
------------------
* class names MUST be CamelCase
* names made by multiple words -- except for classes -- MUST be separated by ``_`` (the underscore character)
* variables and attributes referencing multiple entities MUST be pluralized (except for ``ManyToManyField``\ s, see below)


Stubs
-----

When stubbing callable objects (functions, methods, etc.) you should use ``raise NotImplementedError`` instead of just a
``pass`` statement, as a remainder for you and other developers.


Managed attributes
------------------

To retrieve a computed attribute in class, try to use Python *properties* when possible, instead of *methods*, since
this style provides for improved readability.


Models
------
* Names for ``BooleanField`` and ``NullBooleanField`` model fields SHOULD begin with a verb: e.g. ``is_active``,
  ``can_do_something``, etc.
* *Model validation* and *model save* steps SHOULD be kept distinct, as much as possible; e.g. validation-specific logic
  goes within the ``Model.clean()`` method, while save-time logic goes within ``Model.save()``.  Since ``Model.clean()``
  doesn't get automatically called, usually ``Model.save()`` will call it


Fields
------
* When a ``related_name`` attribute of a ``ForeignKey`` or ``ManyToManyField`` model field is specified, it SHOULD end
  with ``_set``, for consistency with Django default behaviour;
* Since ``ManyToManyField`` model fields behave as ``Manager`` objects, like ``related_name`` model attributes
  automatically added by Django to describe reverse relationships between models, for usage consistency their names
  SHOULD end with ``_set``;

* For each ``ManyToManyField`` or ``related_name`` attribute, add a property providing direct access to the full
  QuerySet of corresponding model instances.  Example:

.. sourcecode:: python

   class Author(models.Model):
         ...
         
         @property
         def books(self):
             return self.book_set.all()
   
   class Book(models.Model):
         author_set = ManyToManyField(Author, related_name='book_set')
         ...

         @property
         def authors(self):
             return self.author_set.all()

URLconfs
--------
* URLs MUST end with a ``/`` character

* within URL regexp patterns, *named groups* (e.g. ``(?<pk>\d+)``) should be preferred to un-named ones (e.g. ``(\d+)``)

* Language strings within URLs MUST be in English for *development* setups and in Italian for *production* setups

* URLs pointing to detail pages for objects (e.g. ``DetailView``\ s) SHOULD look like  ``/<object>s/<id>/``, ``/<object>s/<slug>/``, ... (e.g. ``/acts/1/``)

* URLs pointing to pages listing objects *of the same kind* (e.g. ``ListView``\ s) SHOULD look like  ``/<object>s/`` (e.g. ``/acts/``)

* the root URLconf module -- i.e. ``open_municipio.urls`` -- should only contains:
 
 * URLs not associated with any specific application (e.g. ``/info/``)
 * *mount-points* of application-specific URLs (by using Django ``include()`` facility)

* Application-specific URLs go within the ``urls`` module (or package) of the corresponding application

* within URL  patterns, view names:

  * should be prefixed with the string ``om_`` (in order to avoid name clashes with 3-rd party app)
  * use ``_`` instead of ``-`` for separating words


Views
-----
* EVERY view SHOULD be **named** (via the ``name`` parameter of the corresponding URL pattern); this is useful for
  enabling the reverse-lookup mechanisms for URL resolution

* **Class-based** view implementations should be preferred to **function-based** ones


            

Markers
-------

Within source code, you SHOULD use convential (uppercased) keywords to denote specific kind of comments:
 
  * ``TODO`` denotes features to implement, improvements to made, etc.
  * ``FIXME`` denotes issues with the code to be solved later
  * ``WRITEME`` SHOULD be used as a (temporary!) replacement for docstrings, etc.
 


