from django.conf import settings
from django.contrib.auth import login, get_backends
from django.contrib.auth.models import User
from open_municipio.locations.models import Location

from open_municipio.users.forms import UserRegistrationForm
from open_municipio.users.models import UserProfile

from registration.signals import user_registered
from registration.signals import user_activated


"""
Functions listed below act as receivers and are used along the
registration workflow.
"""


def user_created(sender, user, request, **kwargs):
    """
    As soon as a new ``User`` is created, the correspondent
    ``UserProfile`` must be created too. Necessary information is
    supposed to be found in POST data.
    """
    form = UserRegistrationForm(request.POST)
    user.first_name = form.data['first_name']
    user.last_name = form.data['last_name']
    user.save()
    
    extra_data = UserProfile(user=user)
    extra_data.says_is_politician = form.data['says_is_politician'] if 'says_in_politician' in form.data else False
    extra_data.uses_nickname = form.data['uses_nickname'] if 'uses_nickname' in form.data else False
    extra_data.wants_newsletter = False
    extra_data.wants_newsletter = form.data['wants_newsletter'] if 'wants_newsletter' in form.data else False
    extra_data.location = Location.objects.get(pk=form.data['location']) if form.data['location'] != '' else None
    extra_data.description = form.data['description']
    extra_data.image = request.FILES['image']
    extra_data.save()


def log_in_user(sender, user, request, **kwargs):
    """
    Dirty trick to let the user automatically logged-in at the end of
    the registration process.
    """
    if getattr(settings, 'REGISTRATION_AUTO_LOGIN', False):
        backend = get_backends()[0] # A bit of a hack to bypass `authenticate()`.
        user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
        login(request, user)


user_registered.connect(user_created)
user_activated.connect(log_in_user)

