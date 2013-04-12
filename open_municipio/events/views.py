from django.views.generic import TemplateView

from open_municipio.events.models import Event
from open_municipio.people.models import CityCouncil

class EventsYearView(TemplateView):
    template_name = "events/event_council_year.html"

    def get_queryset(self):
        # TODO make this year a dynamic parameter passed to the class instance
        year = 2010
        return Event.objects.filter(institution=CityCouncil().as_institution).filter(date__year=year)
