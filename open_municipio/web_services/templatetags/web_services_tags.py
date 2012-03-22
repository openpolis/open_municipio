from django import template
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.conf import settings
from open_municipio.web_services.models import Sharing

register = template.Library()

@register.inclusion_tag('web_services/share.html', takes_context=True)
def share(context, object, title="", description=""):
    """
    Displays the social bar with facebook, twitter and google-plus icons
    to share the generic object provided
    TODO: Add customization
    """

    if not context['request'].user.is_authenticated():
        return { 'user' : context['request'].user }

    url = ''
    if hasattr(object, 'get_absolute_url'):
        url = getattr(object, 'get_absolute_url')()

    if not url.startswith('http'):
        url = context['request'].build_absolute_uri(url)

    content_type = ContentType.objects.get_for_model(object)
    sharing_count = Sharing.objects.filter(content_type__pk = content_type.pk, object_id = object.pk ).count()
    sharing_save_url = reverse('web_service_share', kwargs={'model': content_type.model, 'app': content_type.app_label, 'object_id' : object.pk })

    return {
        'debug': settings.DEBUG,
        'user' : context['request'].user,
        'object' : object,
        'url' : url,
        'title' : title,
        'description': description,
        'services': settings.WEB_SERVICES,
        'sharing_save_url': sharing_save_url,
        'sharing_count' : sharing_count,
        'STATIC_URL': context['STATIC_URL'],
    }
