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
        'IS_DEMO': settings.IS_DEMO,
#        'GOOGLE_ANALYTICS': settings.WEB_SERVICES['google_analytics'],
        'login_url': url,
    }
