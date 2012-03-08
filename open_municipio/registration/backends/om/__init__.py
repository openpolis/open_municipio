from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site

from registration import signals
from registration.models import RegistrationProfile
from open_municipio.registration.forms import OMRegistrationForm
from registration.backends.default import DefaultBackend
from open_municipio.users.models import UserProfile


class OMBackend(DefaultBackend):
    """
    
    """

    def register(self, request, **kwargs):
        """
        Override of the register method.
        Creates an inactive auth.User record; adds first_name and last_name;
        Also creates a UserProfile record, with some of the compulsory information in it.
        """
        username, email, password = kwargs['username'], kwargs['email'], kwargs['password1']
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)
        new_user = RegistrationProfile.objects.create_inactive_user(username, email, password, site)

        # add first and last name to created inactive user
        new_user.first_name = request.POST['first_name']
        new_user.last_name = request.POST['last_name']
        new_user.save()

        # create
        if 'uses_niuckname' in request.POST:
            uses_nickname = True
        else:
            uses_nickname = False
        new_profile = UserProfile(user=new_user,
                                  city=request.POST['city'],
                                  uses_nickname=uses_nickname)
        new_profile.save()

        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=request)
        return new_user

    def get_form_class(self, request):
        """
        Return the default form class used for user registration.
        """
        return OMRegistrationForm

    def post_activation_redirect(self, request, user):
        """
        Overrides standard behavior and redirect to
        profile editing afer user activation.
        """
        return ('profiles_edit_profile', (), {})
