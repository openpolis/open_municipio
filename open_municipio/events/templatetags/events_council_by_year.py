from django import template
from datetime import date
from open_municipio.people.models import CityCouncil
from open_municipio.events.models import Event

register = template.Library()

@register.assignment_tag
def get_event_years(max_len=5):
    if CityCouncil().as_institution == None:
        return []

    year_dates = Event.objects.filter(institution=CityCouncil().as_institution).dates("date","year","DESC")

    years = map(lambda d: str(d.year), year_dates[0:max_len])
 
    return years

@register.simple_tag
def print_events_council_list(year, month):
    events = Event.objects.filter(institution=CityCouncil().as_institution).filter(date__year=year,date__month=month).dates("date", "day","ASC")

    if len(events) == 0:
        return ""

    today = date.today()
    text = "<div class='event-dates'>"
    for d in events:
        event_class = "event-past"
        if d.date() > today:
            event_class = "event-future"
        text += "<div class='event-date %s'>%s</div>" % (event_class,d.day)
    text += "<div>"
    return text
