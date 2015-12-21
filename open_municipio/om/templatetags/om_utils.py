from django import template
from django.template.defaultfilters import date as _date

from django.utils.safestring import mark_safe

import hashlib

register = template.Library()


def key(d, key_name):
    try:
        value = d[str(key_name)]
    except KeyError:
        from django.conf import settings
        value = "(%s)"%key_name
    return value
key = register.filter('key', key)


@register.filter
def as_token(value, arg='-'):
    """
    This template filter takes a model instance and returns a unique string representation for it.
    
    The string representation is of the form ``<app_label>-<model_name>-<obj_pk>`` where:
    
    * ``<app_label>`` is the "app label" for the model instance
    * ``<model_name>`` is the (lowercased) name of the model
    * ``<obj_pk>`` is the primary key of the model instance
    
    This token may be used for example to tie a Django model instance to a given DOM element,
    by  assignining it to the ``id`` attribute of that element.
           
    The ``arg`` argument, if provided, is used as the internal separator for the object's parameters 
    within the token string (defaulting to the `-` character).
    
    Example usage
    -------------
    
    act = Act.objects.get(pk=1)
    
    {{ act|as_token }} -> "acts-act-1"
    """
    try:
        obj = value
        app_label = obj._meta.app_label
        model_name = obj._meta.object_name.lower()
        token = arg.join([app_label, model_name, str(obj.pk)]) 
        return mark_safe(token)
    except:
        return ''



@register.filter
def circled(value, args=''):
    """
    Surround value with a circle,
    if value is a Date type, has specific styles
    {{ act.presentation_date|circled }}
    {{ act.presentation_date|circled:"full" }}
    {{ act.presentation_date|circled:"colored" }}
    {{ act.presentation_date|circled:"full,colored" }}
    NOTE: Works with .circle styles

    """
    colored = 'colored' in args
    full = 'full' in args
    dark = 'dark' in args
    voteok = 'voteok' in args
    voteko = 'voteko' in args

    classes = []
    if type(value).__name__=='date':
        if full:
            classes.append('circle-fulldate')
            value = "<span class=\"day\">%s</span> <span class=\"month\">%s</span> <span class=\"year\">%s</span>" %\
                    (_date(value, "d"), _date(value, "b"), _date(value, "Y"))
        else:
            classes.append('circle-date')
            value = "<span class=\"day\">%s</span> <span class=\"month\">%s</span>" %\
                    (_date(value, "d"), _date(value, "b"))
    else:
        classes.append('circle')

    if colored:
        classes.append('circle-colored')
    elif dark:
        classes.append('circle-dark')
    elif voteok:
        classes.append('circle-green')
    elif voteko:
        classes.append('circle-red')

    return mark_safe('<div class="%s">%s</div>' %  (' '.join(classes), value))

@register.filter
def one_way(clear_text):

    if isinstance(clear_text, int):
        clear_text = str(clear_text)

    return hashlib.md5(clear_text).hexdigest()
