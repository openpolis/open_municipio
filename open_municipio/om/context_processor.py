from django.conf import settings
from django.utils.http import urlquote
from django.contrib.auth import REDIRECT_FIELD_NAME

def defaults(request):
    '''
    A context processor to add the default site settings to the current Context
    '''

    path = urlquote(request.get_full_path())
    url = '%s?%s=%s' % (settings.LOGIN_URL, REDIRECT_FIELD_NAME, path)

    return {
        'main_city': settings.SITE_INFO['main_city'],
        'main_city_website': settings.SITE_INFO['main_city_website'],
        'beta': settings.SITE_INFO['site_version'],
        'DEBUG': settings.DEBUG,
        'TEMPLATE_DEBUG': settings.TEMPLATE_DEBUG,
        'ALERT_POPUP': settings.ALERT_POPUP,
        'ALERT_BAR': settings.ALERT_BAR,
        'ALERT_NAVBAR': settings.ALERT_NAVBAR,
        'GOOGLE_ANALYTICS': settings.WEB_SERVICES.get('google_analytics', None),
        'login_url': url,
        'UI_LOCATIONS': settings.UI_LOCATIONS,
        'UI_SITTINGS_CALENDAR': settings.UI_SITTINGS_CALENDAR,
        'UI_ALLOW_NICKNAMES': settings.UI_ALLOW_NICKNAMES,
        'SEARCH_URLS': settings.SEARCH_URLS,
        'SOCIAL_SITES': settings.SOCIAL_SITES,       
        'LOGO_URL': getattr(settings, 'LOGO_URL', None)

    }
