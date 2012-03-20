from django import template
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from open_municipio import settings_local

register = template.Library()

@register.inclusion_tag('web_services/share.html', takes_context=True)
def share(context, title, object_or_url="", description=""):
    """
    Displays the social bar with facebook, twitter and google-plus icons
    TODO: Add customization
    """
    content_type = ContentType.objects.get_for_model(object_or_url)
    if hasattr(object_or_url, 'get_absolute_url'):
        url = getattr(object_or_url, 'get_absolute_url')()
    shares = 0 # content_type.objects.filter(content_type__pk=object_or_url.id)
    share_save_url = reverse('web_service_share', kwargs={
        'content_type': content_type.model,
        'object_id' : object_or_url.pk })


    url = unicode(object_or_url)

    if not url.startswith('http'):
        url = context['request'].build_absolute_uri(url)

    return {
        'title' : title,
        'url' : url,
        'description': description,
        'services': settings_local.WEB,
        'server_url': share_save_url,
        'shares' : shares,
        'STATIC_URL': context['STATIC_URL'],
    }
