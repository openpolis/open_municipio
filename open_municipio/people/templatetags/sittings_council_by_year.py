from django import template
from django.db import models
from django.conf import settings
from datetime import date
from django.core.urlresolvers import reverse
from open_municipio.people.models import Institution
from open_municipio.people.models import Sitting

register = template.Library()

@register.assignment_tag
def get_sittings_years(max_len=5):
    if Institution.COUNCIL == None:
        return []

    curr_year = date.today().year

    # FIXME find a way to show all year (even older ones, e.g. with a paginator)
    from_year = max(settings.OM_START_YEAR, curr_year - max_len)

    sitting_years = list(reversed(range(from_year, curr_year + 1)))

    return sitting_years

@register.simple_tag
def print_sittings_council_list(year, month):
    sittings = Sitting.objects.filter(institution__institution_type=Institution.COUNCIL).filter(date__year=year).filter(date__month=month).filter(~ models.Q(idnum__startswith="-")).order_by("date")

    if len(sittings) == 0:
        return ""

    today = date.today()
    text = "<div class='sitting-dates'>"
    for e in sittings:
        sitting_class = "sitting-past"
        if e.date > today:
            sitting_class = "sitting-future"
        text += "<a href='%s'><div class='sitting-date %s'>%s</div></a>" % \
            (e.get_absolute_url(), sitting_class, e.date.day, )
    text += "<div>"
    return text
