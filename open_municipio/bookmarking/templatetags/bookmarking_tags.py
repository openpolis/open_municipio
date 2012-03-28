from django.conf import settings
from django import template
from django.utils.safestring import mark_safe


register = template.Library()

@register.simple_tag(takes_context=True)
def is_key_class(context, obj):
    """
    This template tag takes a (bookmarkable) model instance and returns the CSS class 
    to be applied to the DOM element representing it in order to describe its
    current status (bookmarked or not).
    
    Given an object, the tag output is as follows:
    
    * if the object is a bookmarkable model instance that is currently bookmarked,
      it returns the string provided by ``settings.OM_BOOKMARKING_STAR_CLASS``
    
    * if the object is a bookmarkable model instance that is currently not bookmarked
      AND the user is staff, it returns the string provided by ``settings.OM_BOOKMARKING_EMPTY_STAR_CLASS``
      
    * if the object is a bookmarkable model instance that is currently not bookmarked
      but the user is NOT staff, or the object is not a bookmarkable one, it returns the empty string
      
    """
    try:
        user = context['user'] 
        if obj.is_key:
            return mark_safe(settings.OM_BOOKMARKING_STAR_CLASS)
        elif user.is_staff:
            return mark_safe(settings.OM_BOOKMARKING_EMPTY_STAR_CLASS)
        else:
            return '' 
    except:
        return ''
    