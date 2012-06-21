from django.http import HttpResponseRedirect

from users.models import UserProfile

def create_profile(request, user, response, details, is_new=False, *args, **kwargs):
    if is_new:
        privacy_level = request.session.get('saved_privacy_level')
        wants_newsletter = request.session.get('saved_wants_newsletter')
        city = request.session.get('saved_city')
        profile, created = UserProfile.objects.get_or_create(user=user, defaults={
                'privacy_level': privacy_level,
                'wants_newsletter': wants_newsletter,
                'city': city,
                })
        profile.save()

def extra_data(request, *args, **kwargs):
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

def redirect_to_form(*args, **kwargs):
    if not kwargs['request'].session.get('saved_username') and \
       kwargs.get('user') is None:
        return HttpResponseRedirect('/login-form/')
