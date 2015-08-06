from datetime import datetime, date

from django import template
from django.utils.safestring import mark_safe

from open_municipio.people.models import GroupCharge

register = template.Library()

@register.filter
def get_absent_label(politician):
    return "%s assenze (%.2f %s)" % (politician.n_absent_votations, politician.perc_absences,"%")

@register.filter
def get_rebel_label(politician):
    return "%s ribellioni (%.2f %s)" % (politician.n_rebel_votations, politician.perc_rebel,"%")

@register.filter
def get_current_group(charge, as_of=None):

    if isinstance(as_of, date) or isinstance(as_of, datetime):
        as_of = as_of.strftime("%Y-%m-%d")

    curr_group = None

    try:
        curr_group = charge.current_at_moment_groupcharge(moment=as_of).group
    except Exception:
        # the mayor does not belong to a group, for example ...
        pass

    return curr_group

@register.filter
def group_acronym(group):

    try:
        return mark_safe('<a href="%s">%s</a>' % (group.get_absolute_url(), group.acronym))
    except Exception:
        # the mayor does not belong to a group, for example ...
        return None

@register.filter
def group_name(group):

    try:
        return mark_safe('<a href="%s">%s</a>' % (group.get_absolute_url(), group.name))
    except Exception:
        # the mayor does not belong to a group, for example ...
        return None

@register.filter
def charge_group_acronym(charge, as_of=None):

    try:
        g = get_current_group(charge, as_of)
        return group_acronym(g) if g else ''
    except Exception:
        # the mayor does not belong to a group, for example ...
        return None

@register.filter
def charge_group_name(charge, as_of=None):

    try:
        g = get_current_group(charge, as_of)
        return group_name(g) if g else ''
    except Exception:
        # the mayor does not belong to a group, for example ...
        return None
