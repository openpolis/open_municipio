from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from open_municipio.users.models import UserProfile
from social_auth.utils import setting


"""
Functions listed below are used in ``django-social-auth``
pipeline. Pipeline is the series of steps users walk through to log in
on OpenMunicipio with their social accounts.
"""

def redirect_to_form(*args, **kwargs):
    """
    Non-registered users will be prompted a few questions so that
    their OpenMunicipio account is created.
    """
    if not kwargs['request'].session.get('saved_username') and \
       kwargs.get('user') is None:
        return HttpResponseRedirect(reverse('login-form'))


def extra_data(request, *args, **kwargs):
    """
    Extra data we need to collect to populate user's profile.
    """
    if kwargs.get('user'):
        username = kwargs['user'].username
        profile = kwargs['user'].get_profile()
        wants_newsletter = profile.wants_newsletter
        says_is_politician = profile.says_is_politician
        uses_nickname = profile.uses_nickname
        location = profile.location
    else:
        username = request.session.get('saved_username')
        wants_newsletter = request.session.get('saved_wants_newsletter')
        says_is_politician = request.session.get('saved_says_is_politician')
        uses_nickname = request.session.get('saved_uses_nickname')
        location = request.session.get('saved_location')
    return {
        'username': username,
        'wants_newsletter': wants_newsletter,
        'says_is_politician': says_is_politician,
        'uses_nickname': uses_nickname,
        'location': location,
        }


def create_profile(request, user, response, details, is_new=False, *args, **kwargs):
    """
    Once the user account is created, a profile must be created
    too. (User accounts are Django built-in. Profile is the place we
    store additional information.)
    """
    if is_new:
        wants_newsletter = request.session.get('saved_wants_newsletter')
        says_is_politician = request.session.get('saved_says_is_politician')
        uses_nickname = request.session.get('saved_uses_nickname')
        location = request.session.get('saved_location')
        profile, created = UserProfile.objects.get_or_create(user=user, defaults={
                'wants_newsletter': wants_newsletter,
                'location': location,
                'says_is_politician': says_is_politician,
                'uses_nickname': uses_nickname,
                })
        profile.save()
