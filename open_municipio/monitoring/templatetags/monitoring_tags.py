from django import template

register = template.Library()


@register.inclusion_tag('monitoring/summary.html', takes_context=True)
def object_monitoring(context, object, show_politician=False):

    return {}

@register.inclusion_tag('monitoring/inline.html', takes_context=True)
def object_inline_monitoring(context, object):

    return {}