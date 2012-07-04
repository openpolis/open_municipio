.. -*- mode: rst -*-
 
=========================
Act workflows' management
=========================

.. contents::

Generalities
============

Every act adopted by a given municipality, before being finalized, followed a well defined *iter*, i.e. a process during
which it was evaluated, discussed and -- possibly -- voted by one or more institutional bodies (e.g. City Government,
City Council, Committees).  


Workflows
=========

From a conceptual perspective, an act's iter may be model by a *workflow*: a directed graph whose nodes are called
*statuses*, while links between nodes are called *transitions*.  In other words, a workflow could be described as a
*finite state machine*. Some peculiarities concerning iters followed by acts:

#. Each category of acts (e.g. deliberations, motions, interpellations, etc.) has its own workflow, comprising, among
   other things, the set of allowed statuses and transitions for that kind of act instances;

#. For a given act type, a subset of allowed statuses is special in that, once reached, the act's status cannot be
   changed from that point onwards.  They are called *final statuses* and treated differently from other (non-final)
   statuses.

Below, we describe how acts' workflows are implemented within OpenMunicipio.     

Statuses
--------

Within our data model, an act's status is just a string attribute (named ``status``) of the model instance representing
that act.  Technically, is a ``StatusField``, a custom field class provided by the `django-model-utils`_ 3rd party app.

The set of allowed status for a given act type is defined by a model class attribute, ``STATUS``, whose value is a
``Choice`` instance (another convenience provided by `django-model-utils`_ ).  In our case, the ``Choice`` constructor
is given an iterable of 3-tuples, where each tuple represents an allowed status and it's made of string values denoting
respectively:

* its database-level representation
* the attribute name as which it can be accessed within the source code
* its (translatable) human-readable representation

Final statuses, on the other hand, are declared by setting a class-level attribute named ``FINAL_STATUSES``, an iterable
of 2-tuples defining the database-level and human-readable representation of the given status.

So, for example, the ``acts.Deliberation`` model class define its allowed/final statuses as follows:

.. code-block:: python                

    STATUS = Choices(
        ('PRESENTED', 'presented', _('presented')),
        ('COMMITTEE', 'committee', _('committee')),
        ('COUNCIL', 'council', _('council')),
        ('APPROVED', 'approved', _('approved')),
        ('REJECTED', 'rejected', _('rejected')),
    )


    FINAL_STATUSES = (
            ('APPROVED', _('approved')),
            ('REJECTED', _('rejected')),
        )


Then:
* to access the current status of a given act instance (say ``act``), just access the corresponding attribute:
``instance.<status_name>``.  

* to determine if a given status (among the allowed ones) is final, use the ``is_final_status()`` method. If given an
  string argument, this method will check if that string represents a final status for that kind of act; when invoked
  without arguments, instead, it will check if the *current* status is a final one

* the ``status_is_final`` attribute is a sort of cache field: it will be ``True`` if and only if the given act has
  reached one of its final statuses, ``False`` otherwise.

Transitions
-----------

Within our data model, state transitions are represented by the ``acts.Transition`` model class.  This model stores the
following pieces of information:

* which act a transition refers to (``act`` field)
* the *target status* -- i.e. what's the act's status after a transition happened (``target_status`` field) 
* when the transition happened (``transition_date`` field)
* an optional string denoting the transition type (``symbol`` field)
* an optional votation (a ``votations.Votation`` instance) associated [#]_ with the transition (``votation`` field)
* optional notes describing the transition (``note`` field)

As you could have noted, a transition doesn't track (directly) what the *source status* was (i.e. act's status before the
transition happened).  Given a transition, this information may be inferred by retrieving the *previous* transition [#]_
and reading its ``target_status`` field [#]_.


Design considerations
=====================

Since workflow-related information is spread among different places (i.e. the ``status`` field of concrete acts models/tables
and the DB table underlying the ``Transition`` model), we need to devise a mechanism to keep them in sync. In
particular, we need to deal with both of these scenarios:

#. A transition instance is added/modified/deleted, so the corresponding act's status must be updated
#. The status of an act instance is updated, so a new transition must be created

In order to simplify the business logic, we should choose an authoritative source of information and update the other
one accordingly. Allowing independent modifications from both sides introduces a significan complexity overhead.

If an act's status changes, we only have two pieces of information at our disposal: the source and target status.  We
neither know when the transition happened (in the real world) nor what kind of transition was, etc.  Sure, we could add
these details by hand, but is cumbersome and we would have to remember to do it every time: otherwise, that status
change will not be recorded by a corresponding transition record.

So, the right way to approach the problem seems to be transition-side-of-things: when a transition is
added/modified/deleted, the corresponding act's status should be modified accordingly and automatically.  This could be
accomplished either via a signal handler (``post_save`` or ``post_delete``) or, better, via overriden ``save()`` and
``delete()`` model instance methods.

There is one left problem, however: what happen if an act's ``status`` field is modified directly? In that case, the
whole machinery would be by-passed, opening the door to a potential data integrity loss.  The optimal solution could be
renaming the ``status`` field -- making it a "private" attribute -- and defining a read-only ``status`` property.









.. _`django-model-utils`: https://bitbucket.org/carljm/django-model-utils/overview


.. rubric:: Notes

.. [#] Since some kind of act transitions are triggered by a ballot.
.. [#] Ordering by the ``transition_date`` field.
.. [#] Since, by definition, the *source status* for a given transition matches the target status for the previous one.
