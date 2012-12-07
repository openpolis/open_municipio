from django.conf import settings

def defaults(request):
    '''
    A context processor to add the default site settings to the current Context
    '''
    return {
        'main_city': settings.SITE_INFO['main_city'],
        'beta': settings.SITE_INFO['site_version'],
        'DEBUG': settings.DEBUG,
        'TEMPLATE_DEBUG': settings.TEMPLATE_DEBUG,
        'IS_DEMO': settings.IS_DEMO,
        'GOOGLE_ANALYTICS': settings.WEB_SERVICES['google_analytics'],
    }
