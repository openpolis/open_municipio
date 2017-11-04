# coding=utf-8

from django import template
from django.core.exceptions import ObjectDoesNotExist
from open_municipio.monitoring.forms import MonitoringForm

register = template.Library()

@register.inclusion_tag('monitoring/summary.html', takes_context=True)
def object_monitoring(context, object, show_politicians=True):

    object_type = object._meta.verbose_name
    if object_type.lower() == 'tag':
        object_type = "l'argomento"
    if object_type.lower() == 'categoria':
        object_type = "la categoria"
    if object_type.lower() == 'persona':
        object_type = "il politico"
    if object_type.lower() in ['delibera', 'mozione', 'interrogazione', 'interpellanza']:
        object_type = "l'atto"


    args = {
        'object': object,
        'object_type': object_type,
#        'user': context['user'],
        'user_profile': context['user_profile'],
        'is_user_monitoring': False,
        'show_politicians': show_politicians,
        'login_url_with_redirect': context['login_url'],
    }
    # is the user monitoring the act?
    try:
        if args['user_profile']: #.is_authenticated():
            # add a monitoring form, to context,
            # to switch monitoring on and off
            args['monitoring_form'] = MonitoringForm(data = {
                'content_type_id': object.content_type_id,
                'object_pk': object.id,
                'user_id': args['user_profile'].user_pk #id
            })

#            if object in args['user'].get_profile().monitored_objects:
            if object in args['user_profile'].monitored_objects:

                args['is_user_monitoring'] = True
    except ObjectDoesNotExist:
        args['is_user_monitoring'] = False

    return args


@register.inclusion_tag('monitoring/inline.html', takes_context=True)
def object_inline_monitoring(context, object, shows_monitoring_users=True):
    args = {
        'object': object,
        'shows_monitoring_users': shows_monitoring_users,
#        'user': context['user'],
        'user_profile': context['user_profile'],
        'is_user_monitoring': False,
        'login_url_with_redirect': context['login_url'],
    }
    # is the user monitoring the act?
    try:
        if args['user_profile']: #.is_authenticated():
            # add a monitoring form, to context,
            # to switch monitoring on and off
            args['monitoring_form'] = MonitoringForm(data = {
                'content_type_id': object.content_type_id,
                'object_pk': object.id,
                'user_id': args['user_profile'].user_pk #id
            })

#            if object in args['user'].get_profile().monitored_objects:
            if object in args['user_profile'].monitored_objects:
                args['is_user_monitoring'] = True
    except ObjectDoesNotExist:
        args['is_user_monitoring'] = False

    return args

@register.inclusion_tag('monitoring/latest_users.html', takes_context=True)
def latest_users(context, users, users_number=20):
    return { "users": users.filter(user__is_active=True).order_by('-user__date_joined')[:users_number] }
