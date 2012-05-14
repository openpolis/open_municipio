from django.core.exceptions import ObjectDoesNotExist
from open_municipio.monitoring.forms import MonitoringForm

__author__ = 'joke2k'

from django import template

register = template.Library()



@register.inclusion_tag('monitoring/summary.html', takes_context=True)
def object_monitoring(context, object, show_politicians=False):
    args = {
        'object': object,
        'user': context['user'],
        'is_user_monitoring': False,
        'show_politicians': show_politicians
    }
    # is the user monitoring the act?
    try:
        if args['user'].is_authenticated():
            # add a monitoring form, to context,
            # to switch monitoring on and off
            args['monitoring_form'] = MonitoringForm(data = {
                'content_type_id': object.content_type_id,
                'object_pk': object.id,
                'user_id': args['user'].id
            })

            if object in args['user'].get_profile().monitored_objects:
                args['is_user_monitoring'] = True
    except ObjectDoesNotExist:
        args['is_user_monitoring'] = False

    return args


@register.inclusion_tag('monitoring/inline.html', takes_context=True)
def object_inline_monitoring(context, object):
    args = {
        'object': object,
        'user': context['user'],
        'is_user_monitoring': False
    }
    # is the user monitoring the act?
    try:
        if args['user'].is_authenticated():
            # add a monitoring form, to context,
            # to switch monitoring on and off
            args['monitoring_form'] = MonitoringForm(data = {
                'content_type_id': object.content_type_id,
                'object_pk': object.id,
                'user_id': args['user'].id
            })

            if object in args['user'].get_profile().monitored_objects:
                args['is_user_monitoring'] = True
    except ObjectDoesNotExist:
        args['is_user_monitoring'] = False

    return args

