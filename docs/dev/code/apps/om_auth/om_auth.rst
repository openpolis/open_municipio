=====================
Om_auth documentation
=====================

.. contents::


Introduction
============

Registering a new account can be a tedious task, sometimes involving
large forms to be filled in and new passwords to remember.

Hence, django-social-auth_ is used to speed up the registration
process. Users can rely on their own social network accounts to enter
OpenMunicipio.

Users may still be asked some extra information which is not provided
by social networks.


.. _django-social-auth: https://github.com/omab/django-social-auth/


Configuration
=============

Once ``django-social-auth`` is installed, some configuration files
must be edited.

----

In ``settings.py``, add ``django-social-auth`` and our custom
``om_auth`` to the list of ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = (
        ....
        'social_auth',
        'open_municipio.om_auth',
    )


Add the needed authentication backends:

.. code-block:: python

    AUTHENTICATION_BACKENDS = (
        'social_auth.backends.twitter.TwitterBackend',
        'social_auth.backends.facebook.FacebookBackend',
        'social_auth.backends.google.GoogleOAuth2Backend',
        'social_auth.backends.contrib.github.GithubBackend',
        'social_auth.backends.OpenIDBackend',
        'django.contrib.auth.backends.ModelBackend',
    )

Add the following lines:

.. code-block:: python

    TEMPLATE_CONTEXT_PROCESSORS = (
        ....
        'social_auth.context_processors.social_auth_by_name_backends',
        'social_auth.context_processors.social_auth_backends',
        'social_auth.context_processors.social_auth_by_type_backends',
    )


Add the following lines:

.. code-block:: python

    # "django-social-auth" settings
    FACEBOOK_EXTENDED_PERMISSIONS = ['email'] # if this is missing, only username is retrieved
    LOGIN_URL = '/login/'
    LOGIN_REDIRECT_URL = '/'
    LOGIN_ERROR_URL = '/login-error/'
    SOCIAL_AUTH_COMPLETE_URL_NAME  = 'socialauth_complete'
    SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'socialauth_associate_complete'
    SOCIAL_AUTH_EXPIRATION = 'expires'
    SOCIAL_AUTH_RAISE_EXCEPTIONS = DEBUG
    SOCIAL_AUTH_PIPELINE = (
        'social_auth.backends.pipeline.social.social_auth_user',
        'social_auth.backends.pipeline.associate.associate_by_email',
        'social_auth.backends.pipeline.misc.save_status_to_session',
        'om_auth.pipeline.redirect_to_form',
        'om_auth.pipeline.extra_data',
        'social_auth.backends.pipeline.user.create_user',
        'om_auth.pipeline.create_profile',
        'social_auth.backends.pipeline.social.associate_user',
        'social_auth.backends.pipeline.social.load_extra_data',
        'social_auth.backends.pipeline.user.update_user_details',
    )

The pipeline is where you adjust ``django-social-auth`` workflow to
your specific needs. More details shortly.

----

In the file ``settings_local.py``, add the following lines:

.. code-block:: python

    TWITTER_CONSUMER_KEY         = ''
    TWITTER_CONSUMER_SECRET      = ''
    FACEBOOK_APP_ID              = ''
    FACEBOOK_API_SECRET          = ''
    GOOGLE_OAUTH2_CLIENT_ID      = ''
    GOOGLE_OAUTH2_CLIENT_SECRET  = ''

Each social network requires an authentication key (within quotation
marks). Refer to the specific social network developer page to
generate the key.


Pipeline
========

The pipeline is a list of functions that define ``django-social-auth``
behaviour. They are processed sequentially. The standard set of
functions can be modified to obtain a custom behaviour.

.. code-block:: python

    SOCIAL_AUTH_PIPELINE = (
        'social_auth.backends.pipeline.social.social_auth_user',
        'social_auth.backends.pipeline.associate.associate_by_email',
        'social_auth.backends.pipeline.misc.save_status_to_session',
        'om_auth.pipeline.redirect_to_form',
        'om_auth.pipeline.extra_data',
        'social_auth.backends.pipeline.user.create_user',
        'om_auth.pipeline.create_profile',
        'social_auth.backends.pipeline.social.associate_user',
        'social_auth.backends.pipeline.social.load_extra_data',
        'social_auth.backends.pipeline.user.update_user_details',
    )

``social_auth.backends.*`` are provided by ``django-social-auth``
itself and documented on the `Authentication Pipeline section`_.

.. note::

    ``social_auth.backends.pipeline.misc.save_status_to_session`` is
    used to store data into session, so that the standard workflow can
    be broken and resumed later with no data-loss.

``om_auth.pipeline.*`` entries are OpenMunicipio custom
functions. Source code can be found in ``om_auth/pipeline.py``.

.. _redirect-to-form-label:

.. function:: om_auth.pipeline.redirect_to_form(*args, **kwargs)
	
    This function redirect the user, during the registration process,
    to a form where he's asked for the extra data needed (and not
    provided by the user's social account) to create a profile in
    OpenMunicipio database. After filling the form and submitting it,
    the user is redirected to the URL
    "..../complete/<name-of-the-used-backend>/"; this trigger the
    resuming of the pipeline one step forward to the
    “social_auth.backends.pipeline.misc.save_status_to_session” step
    (in this case, this very step). Now, in the second iteration of
    this step, the IF cicle is bypassed and the pipeline continues to
    the next step.

.. function:: om_auth.pipeline.extra_data(*args, **kwargs)
	
    This function initialize the extra data collect in the previous
    step and pass them to the next pipeline's step.

.. function:: om_auth.pipeline.create_profile(request, user, response, details, is_new=False, *args, **kwargs)
	
    This function is called after the user creation (which is
    performed by the “default” pipeline's step
    ``social_auth.backends.pipeline.user.create_user``) and creates
    the new user's profile in the database. Usually
    *django-social-auth* makes the built-in user account, but
    OpenMunicipio needs additional data (previously required by the
    form at :ref:`this step <redirect-to-form-label>`) to be stored in
    the user's profile.


.. _`Authentication Pipeline section`: https://github.com/omab/django-social-auth#authentication-pipeline 


API
===

Fields
-------


Methods
----------
.. function:: login_done(request)
	
    return a redirect to user's detail page (use the ``get_profile()``
    `method`_ of the User class)

.. function:: login_error(request)
	
    render the template ``error.html`` (can be founded in the `om_auth
    template directory`_),
	
.. function:: logout(request)
	
    call the ``logout`` function from the `django.contrib.auth`_
    module, then return a redirect to the root web directory.

.. function:: login_form(request)

    called at the “om_auth.pipeline.redirect_to_form” pipeline's
    step. During its first iteration, the IF statement isn't met, so
    this function renders the ``form.html`` template, and stores the
    extra user's data inserted into the form. At this time, the IF
    statement results “true”, so now the function saves the user's
    data in the session and redirect the flow to URL
    "..../complete/<name-of-the-used-backend>/". By default, this URL
    resume the pipeline workflow.
	


.. _`method`: https://docs.djangoproject.com/en/dev/topics/auth/#django.contrib.auth.models.User.get_profile
.. _`om_auth template directory`: https://github.com/openpolis/open_municipio/blob/django-social-auth-dev/open_municipio/templates/om_auth/error.html
.. _`django.contrib.auth`: https://docs.djangoproject.com/en/dev/topics/auth/#django.contrib.auth.logout


