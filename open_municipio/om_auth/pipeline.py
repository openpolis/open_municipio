from django.http import HttpResponseRedirect

from users.models import UserProfile


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
        return HttpResponseRedirect('/login-form/')


def extra_data(request, *args, **kwargs):
    """
    Extra data we need to collect to populate user's profile.
    """
    if kwargs.get('user'):
        username = kwargs['user'].username
        profile = kwargs['user'].get_profile()
        privacy_level = profile.privacy_level
        wants_newsletter = profile.wants_newsletter
        city = profile.city
    else:
        username = request.session.get('saved_username')
        privacy_level = request.session.get('saved_privacy_level')
        wants_newsletter = request.session.get('saved_wants_newsletter')
        city = request.session.get('saved_city')
    return {
        'username': username,
        'privacy_level': privacy_level,
        'wants_newsletter': wants_newsletter,
        'city': city,
        }


def create_profile(request, user, response, details, is_new=False, *args, **kwargs):
    """
    Once the user account is created, a profile must be created
    too. (User accounts are Django built-in. Profile is the place we
    store additional information.)
    """
    if is_new:
        privacy_level = request.session.get('saved_privacy_level')
        wants_newsletter = request.session.get('saved_wants_newsletter')
        city = request.session.get('saved_city')
        profile, cretaed = UserProfile.objects.get_or_create(user=user, defaults={
                'privacy_level': privacy_level,
                'wants_newsletter': wants_newsletter,
                'city': city,
                })
        profile.save()
