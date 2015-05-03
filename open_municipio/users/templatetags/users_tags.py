from django import template
from django.conf import settings
from django.contrib.auth.models import User
from open_municipio.users.models import UserProfile

register = template.Library()

@register.filter
def get_profile_image(obj):

    profile = None
    person = None

    if isinstance(obj, User):
        profile = obj.userprofile
    elif isinstance(obj, UserProfile):
        profile = obj
    else:
        raise ValueError("Unable to get a profile image from '%s'" % obj)

    person = profile.person

    img = None
    if person and person.img:
        img = person.img
    elif profile.image:
        img = profile.image
    
#    print "found: %s" % img

    return img
