from django.views.generic import TemplateView, DetailView, ListView
from django.core.exceptions import ObjectDoesNotExist

from open_municipio.events.models import Event
from open_municipio.people.models import Institution
from open_municipio.acts.models import Act
from open_municipio.speech.models import Speech

class EventDetailView(DetailView):
    model = Event
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)

        events = Event.objects.filter(institution__institution_type=Institution.COUNCIL)

        extra_context = {
            'events' : events,
        }

        context.update(extra_context)
        return context

class EventsYearView(TemplateView):
    template_name = "events/event_council_year.html"

    def get_queryset(self):
        # TODO make this year a dynamic parameter passed to the class instance
        year = 2010
        return Event.objects.filter(institution__institution_type=Institution.COUNCIL).filter(date__year=year)

    def get_context_data(self, **kwargs):
        context = super(EventsYearView, self).get_context_data(**kwargs)

        events = Event.objects.filter(institution__institution_type=Institution.COUNCIL)

        extra_context = {
            'events' : events,
        }

        context.update(extra_context)
        return context

class EventActSpeechesView(ListView):
    model = Speech
    template_name = "events/event_speech_list.html"
    event = None

    def get_queryset(self):
        # set the event object
        pk = self.kwargs["pk"]
        self.event = Event.objects.get(pk=pk)

        # set the act object
        act_pk = self.kwargs["act_pk"]
        self.act = Act.objects.get(pk=act_pk)

        # return the related speeches
        res = Speech.objects.filter(act__pk=act_pk)
    
        print "found %s" % res
        return res


    def get_context_data(self, **kwargs):
        context = super(EventActSpeechesView, self).get_context_data(**kwargs)

        extra_context = {
            'event' : self.event,
            'act' : self.act,
        }

        context.update(extra_context)
 
        return context
