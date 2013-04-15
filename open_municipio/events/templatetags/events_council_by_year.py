from django import template
from datetime import date
from django.core.urlresolvers import reverse
from open_municipio.people.models import Institution
from open_municipio.events.models import Event

register = template.Library()

@register.assignment_tag
def get_event_years(max_len=5):
    if Institution.COUNCIL == None:
        return []

    year_dates = Event.objects.filter(institution__institution_type=Institution.COUNCIL).dates("date","year","DESC")

    years = map(lambda d: str(d.year), year_dates[0:max_len])
 
    return years

@register.simple_tag
def print_events_council_list(year, month):
    events = Event.objects.filter(institution__institution_type=Institution.COUNCIL).filter(date__year=year).filter(date__month=month).order_by("date")

    if len(events) == 0:
        return ""

    today = date.today()
    text = "<div class='event-dates'>"
    for e in events:
        event_class = "event-past"
        if e.date > today:
            event_class = "event-future"
        text += "<a href='%s'><div class='event-date %s'>%s</div></a>" % \
            (reverse("om_event_detail", args=(e.pk, )),event_class,e.date.day)
    text += "<div>"
    return text
