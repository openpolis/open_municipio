from django import template
from django.utils.safestring import mark_safe


register = template.Library()

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

    classes = []
    if type(value).__name__=='date':
        if full:
            classes.append('circle-fulldate')
            value = value.strftime('<span class="day">%d</span> <span class="month">%b</span> <span class="year">%Y</span>')
        else:
            classes.append('circle-date')
            value = value.strftime('<span class="day">%d</span> <span class="month">%b</span>')
    else:
        classes.append('circle')

    if colored:
        classes.append('circle-colored')

    if dark:
        classes.append('circle-dark')

    return mark_safe('<div class="%s">%s</div>' %  (' '.join(classes), value))
