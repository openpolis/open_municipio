from django.views.generic import TemplateView, DetailView, ListView
from django.core.exceptions import ObjectDoesNotExist

from open_municipio.events.models import Event
from open_municipio.people.models import Institution
from open_municipio.acts.models import Act
from open_municipio.speech.models import Speech
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
    
#        print "found %s" % res
        return res


    def get_context_data(self, **kwargs):
        context = super(EventActSpeechesView, self).get_context_data(**kwargs)

        extra_context = {
            'event' : self.event,
            'act' : self.act,
        }

        context.update(extra_context)
 
        return context
