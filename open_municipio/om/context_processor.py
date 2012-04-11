from django.conf import settings

def defaults(request):
    '''
    A context processor to add the default site settings to the current Context
    '''
    return settings.SITE_INFO