=======================
open_municipio.om_utils
=======================

Slug management
===============

.. py:currentmodule:: open_municipio.om_utils.models

Django applications often require a mechanism for automatically generating *slugs* [#]_ for one or more models they
provide.  Django provides a `SlugField`_ for storing (and validating) slugs, but leaves to you the actual task of
generating and saving the slug, when  it's not provided at instance creation time, which is usually the case. 

So, you usually need to provide additional logic for slug generation and saving for each model which declares a
:py:class:`SlugField`, which is not very DRY.  The purpose of :py:class:`SlugModel` is to provide reusable
slug-management logic for this kind of models.


.. _`SlugField`: https://docs.djangoproject.com/en/1.3/ref/models/fields/#slugfield

Design considerations
---------------------

A robust and useful slug-management tool should satisfy at least the following requirements:

#. when a model instance is *created*, a slug should be automatically generated and passed to the :py:class:`SlugField`,
   unless a value has been manually set;
#. it should ensure slug uniqueness (no two model instances can share the same slug)
#. it should allow for custom slug-generation logic


Implementation
--------------

:py:class:`SlugModel` is an abstract Django model class, declaring a :py:class:`SlugField` named ``slug`` and featuring
an overrided :py:meth:`save` method.  When a new instance of a model inheriting from :py:class:`SlugModel` is about to
be created, :py:meth:`save` will generate a new slug -- invoking the :py:meth:`.calculate_slug` -- assign it to the
:py:data:`slug` field, and save that instance to the DB.  

The default implementation of :py:meth:`.calculate_slug` relies on :py:func:`django.template.defaultfilters.slugify`,
appending a numerical suffix if needed, in order to avoid name clashes.

Usage
-----

If you need to define a model class featuring a slug field, just subclass :py:class:`SlugModel` and it should work
out-of-the-box.

.. note::

   Currently, if you use this model as a base class, the model field storing the slug would be named ``slug``.  If you
   need a custom name for the :py:class:`SlugField`, you are out of luck ;-)

If you need to implement a custom logic for slugs' generation, just ovveride the :py:meth:`._slugify` method.

API
---

The public API for this tool comprises just an abstract model, :py:class:`SlugModel`.

Models
~~~~~~
.. py:module:: open_municipio.om_utils.models

.. py:class:: SlugModel   
   
    An abstract base class encapsulating data & logic shared by models needing a :py:class:`SlugField`.

    .. py:method::  calculate_slug([base=None])
       
        Convert an arbitrary string ``base`` into another one, suitable to be used as a slug.
        
        If the calculated slug already exists in the DB, add a numerical suffix until is OK.

        If the ``base`` argument is not provided, the source string default to the :py:data:`name` attribute
        of the given model instance. If no :py:data:`name` attribute is defined, neither, raise a :py:exc:`TypeError`.

    .. py:method:: _slugify(base, i=None)

       Take a string and return a "slugified" version of it, optionally appending a numerical suffix.
       
       :param string base: the base string
       :param integer i: a numerical suffix to append to the "slugified" string
       :return: the "slugified" string
    
    


Linked lists
============


Motivations
-----------

In a Django application, one may need to build a data structure which is a linked list [#]_ of model instances, in order
to make it persistent by storing it within that application's database.  For example, within OpenMunicipio both the
:py:class:`Transition` and :py:class:`InstitutionCharge` models have a natural structure of (double-)linked lists.          

Building, navigating and maintaining referential integrity of linked list of model instances requires a fair share of
custom logic which, however, is largely common to every model of this kind.  So, a DRY approach would be to encapsulate
that custom logic into an abstract model, to be used as a base class by every concrete model representing a node of a
linked list data structure.  This is what :py:class:`LinkedListNode` is intended to do.

Design considerations
---------------------

In order to store pointers to the previous/next node, each node instance needs to declare two :py:class:`ForeignKey`\s.
At the database level, these fields are represented by two integer columns, storing the ID to the previous/next node's
record in the same table.  Due to inherent properties of linked lists, these two DB columns must satisfy the following
requirements:

#. Each ID may appear at most one time (since each node may be pointed to by at most another node)
#. They must allow for ``NULL`` values (think to the first and last nodes)

These requirements maps to the following one at the Django ORM level:

#. The :py:class:`ForeignKey`\s must actually be :py:class:`OneToOneField`\s pointing to ``'self'`` -- a so-called `recursive
   relationship`_
#. They should be nullable -- i.e. their constructor should be passed ``null=True`` and ``blank=True``.


Actually, taking into account that Django automagically add a "reversed" accessor field (as specified by the
``related_name`` argument), only one :py:class:`OneToOneField` needs to be declared in the model class.

Now, the question arises where to place this :py:class:`OneToOneField`, wheter on the base, abstract model or the
concrete one.  If we choose the first approach, we'd have to hard-code the name of "pointer" fields, which is not
desiderable.  So, it's better to declare the :py:class:`OneToOneField` on the concrete model class: it's a little less
DRY, but more flexible.

Usage
-----

In order to use the :py:class:`LinkedListNode` model, just follow these steps:

#. Declare the concrete model as a subclass of :py:class:`LinkedListNode` (which, in turn, is a subclass of
   :py:class:`models.Model`);

#. Within your model, declare a :py:class:`OneToOneField` pointing to ``'self'`` and having ``null=True`` and
   ``blank=True``; this will hold the pointer to the next node.  Remember to set the ``related_name`` argument: its
   value will be the name for the reverse accessor of :py:class:`OneToOneField` (that holding the pointer to the previous
   node);

.. #. add a ``pointer_next`` option the ``Meta`` subclass of your model; this is needed so that :py:class:`LinkedListNode`
..    will be able to tell which model field holds the "next" pointer -> DON'T WORK



.. _`recursive relationship`: https://docs.djangoproject.com/en/1.3/ref/models/fields/#recursive-relationships



API
---

Models
~~~~~~

.. py:class:: LinkedListNode
 
    An abstract model class representing a node of a (double-)linked list of model instances.
    
    It encapsulates generic data & logic that can be used to manage such data stuctures, including:
    
      * linked list navigation
      * addition/removal of list nodes

Managers
~~~~~~~~

Signal handlers
~~~~~~~~~~~~~~~


.. rubric:: Footnotes

.. [#] With the term *slug* we mean an *URL-safe* string -- i.e. a string only containing characters which can be safely
       included within an URL, i.e. alphanumeric characters plus the hyphen (``-``).

.. [#] A *linked list* is a data strucure made of elements (usually called *nodes*) each of which -- except the last one
       -- has a pointer to (and is pointed by) just another element. This way, every node (except the last one) has a
       node coming after it, sometimes called the *next node*. If each node -- except the first one,  of course -- also
       stores a pointer to its *previous node* (i.e. the node that it's being pointed by) we have what is called a
       *double-linked list*.  We refer to the first node of a linked list as the *head* of that list, while the last
       node will be the list's *tail*.




