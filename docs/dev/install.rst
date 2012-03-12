.. -*- mode: rst -*-
 
========================================
Installing and configuring OpenMunicipio
========================================

.. contents::

Overview
========

This document is a step-by-step tutorial describing how to install and configuring a working instance of *OpenMunicipio*  

Requirements
============
Since *OpenMunicipio* is built on the top of the Django_ web development framework first of all you need to make sure
that your OS environment satisfy the `corresponding requirements`_.

Following a widespread good practice in the Python community, we strongly encourage you to make use of the powerful
`virtualenv`_ tool, allowing the creation of isolated Python runtime environments.

An handy companion for `virtualenv` is `virtualenvwrapper`_,  a set of scripts providing a few smart facilities to
simplify creation and management of Python virtual environments.

Once installed a Python package manager (we strongly suggest `pip`_), you can install `virtualenv` and
`virtualenvwrapper` as follows:

.. sourcecode:: bash

 # pip install virtualenv virtualenvwrapper


..  _Django: http://djangoproject.com/
.. _`corresponding requirements`: http://docs.djangoproject.com/en/dev/faq/install/
.. _`virtualenv`: http://pypi.python.org/pypi/virtualenv
.. _`virtualenvwrapper`: http://www.doughellmann.com/docs/virtualenvwrapper/
.. _`pip`: http://pip.readthedocs.org/

