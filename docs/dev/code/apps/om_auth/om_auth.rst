=======================
 Om_auth documentation
=======================

.. contents::


Introduction
============
When a user wants to create an account in OpenMunicipio, usually he must compile a form with all his needed data.
But, thanks to *django-social-auth*, it is possible to shorten this procedure by retrieving all the needed data stored in user's external social accounts (like Facebook, Twitter or Google).
The *om_auth* application is a customization of the `django-social-auth`_ application.



.. _`django-social-auth`: https://github.com/omab/django-social-auth/


Configuration
=============
Once *django-social-auth* is installed, some configuration files must be edited.

----

In the file **settings.py**:

Add the following 2 lines into the INSTALLED APPS configuration to enable the *django-social-auth* application and our custom *om_auth* application:

.. code-block:: python

    INSTALLED_APPS = (
        ....
        ....
        ....
        'social_auth',
        'open_municipio.om_auth',
    )


Add the following lines to enable the social login via the most used social networks:

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
    FACEBOOK_EXTENDED_PERMISSIONS = ['email']   # this line is needed to retrieve the user's email from facebook; otherwise, only username is retrieved. 
    LOGIN_URL          = '/login/'
    LOGIN_REDIRECT_URL = '/'
    LOGIN_ERROR_URL    = '/login-error/'
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

.. note::

    The pipeline is the core of *django-social-auth* working. It's a worflow of functions, and it's possible to interrupt this workflow to add customizing functions, to cover all the specific cases. In our case, we added the following steps:

    .. code-block:: python
     
        ....
        'om_auth.pipeline.redirect_to_form',
        'om_auth.pipeline.extra_data',
        ....   
        'om_auth.pipeline.create_profile',
        ....

----

In the file **settings_local.py**:

Add the following lines:

.. code-block:: python

    # `django-social-auth` configuration
    TWITTER_CONSUMER_KEY         = ''
    TWITTER_CONSUMER_SECRET      = ''
    FACEBOOK_APP_ID              = ''
    FACEBOOK_API_SECRET          = ''
    GOOGLE_OAUTH2_CLIENT_ID      = ''
    GOOGLE_OAUTH2_CLIENT_SECRET  = ''

Between the quotation marks, put the alphanumeric keys that each social network provided when the OpenMunicipio application was registered with them.


Pipeline
========
*Django-social-auth* works with the concept of *pipeline*, where a list of function is called and processed one after the other.
The default pipeline can be interrupted and additional custom step can be added at will. Our custom pipeline is defined in the ``settings.py`` file. Here it is:

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


All the 'social_auth.backends' functions belong to the default pipeline and are well explained in the documentation at the github repository of *django-social-auth*, in the `Authentication Pipeline section`_.

.. note::
    Pay attention to the “social_auth.backends.pipeline.misc.save_status_to_session” step: it's used to store the useful data into the user's session, ready to be retrieved when needed.
    In this way, it's possible, for example, to interrupt the normal pipeline, redirect the user to a form where additional data are asked, and then resume the normal pipeline's workflow. 

Few lines in the *pipeline* are named 'om_auth.pipeline' and those are the custom functions for the OpenMunicipio project, coded in the ``om_auth/pipeline.py`` file.
Let's see them in detail:

.. _redirect-to-form-label:

.. function:: om_auth.pipeline.redirect_to_form(*args, **kwargs)
	
    This function redirect the user, during the registration process, to a form where he's asked for the extra data needed (and not provided by the user's social account) to create a profile in OpenMunicipio database. After filling the form and submitting it, the user is redirected to the URL "..../complete/<name-of-the-used-backend>/"; this trigger the resuming of the pipeline one step forward to the “social_auth.backends.pipeline.misc.save_status_to_session” step (in this case, this very step). Now, in the second iteration of this step, the IF cicle is bypassed and the pipeline continues to the next step.

.. function:: om_auth.pipeline.extra_data(*args, **kwargs)
	
    This function initialize the extra data collect in the previous step and pass them to the next pipeline's step.

.. function:: om_auth.pipeline.create_profile(request, user, response, details, is_new=False, *args, **kwargs)
	
    This function is called after the user creation (which is performed by the “default” pipeline's step ``social_auth.backends.pipeline.user.create_user``) and creates the new user's profile in the database. Usually *django-social-auth* makes the built-in user account, but OpenMunicipio needs additional data (previously required by the form at :ref:`this step <redirect-to-form-label>`) to be stored in the user's profile.



.. _`Authentication Pipeline section`: https://github.com/omab/django-social-auth#authentication-pipeline 


API
===

Fields
-------


Methods
----------
.. function:: login_done(request)
	
    return a redirect to user's detail page (use the ``get_profile()`` `method`_ of the User class)

.. function:: login_error(request)
	
    render the template ``error.html`` (can be founded in the `om_auth template directory`_), 
	
.. function:: logout(request)
	
    call the ``logout`` function from the `django.contrib.auth`_ module, then return a redirect to the root web directory.

.. function:: login_form(request)

    called at the “om_auth.pipeline.redirect_to_form” pipeline's step. During its first iteration, the IF statement isn't met, so this function renders the ``form.html`` template, and stores the extra user's data  inserted into the form. At this time, the IF statement results “true”, so now the function saves the user's data in the session and redirect the flow to URL "..../complete/<name-of-the-used-backend>/". By default, this URL resume the pipeline workflow.
	


.. _`method`: https://docs.djangoproject.com/en/dev/topics/auth/#django.contrib.auth.models.User.get_profile
.. _`om_auth template directory`: https://github.com/openpolis/open_municipio/blob/django-social-auth-dev/open_municipio/templates/om_auth/error.html
.. _`django.contrib.auth`: https://docs.djangoproject.com/en/dev/topics/auth/#django.contrib.auth.logout


