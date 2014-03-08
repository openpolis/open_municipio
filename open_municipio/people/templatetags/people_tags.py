from datetime import datetime, date

from django import template

from open_municipio.people.models import GroupCharge

register = template.Library()

@register.filter
def get_absent_label(politician):
    return "%s assenze (%.2f %s)" % (politician.n_absent_votations, politician.perc_absences,"%")

@register.filter
def get_rebel_label(politician):
    return "%s ribellioni (%.2f %s)" % (politician.n_rebel_votations, politician.perc_rebel,"%")

@register.filter
def get_current_group(charge, as_of):

    if isinstance(as_of, date) or isinstance(as_of, datetime):
        as_of = as_of.strftime("%Y-%m-%d")

    curr_group = None

    try:
        curr_group = charge.current_at_moment_groupcharge(moment=as_of).group
    except Exception:
        # the mayor does not belong to a group, for example ...
        pass

    return curr_group
