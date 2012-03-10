from django.views.generic import DetailView
from django.core.exceptions import ObjectDoesNotExist
from os import sys
from open_municipio.people.models import Institution, Person
from open_municipio.monitoring.forms import MonitoringForm


class InstitutionDetailView(DetailView):
    model = Institution
    context_object_name = 'institution'


class PersonDetailView(DetailView):
    model = Person
    context_object_name = 'person'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(PersonDetailView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the institutions
        context['institution_list'] = Institution.objects.all()

        print  >> sys.stderr, "context: %s" % context

        # is the user monitoring the act?
        context['is_user_monitoring'] = False
        try:
            if self.request.user.is_authenticated():
                # add a monitoring form, to context,
                # to switch monitoring on and off
                context['monitoring_form'] = MonitoringForm(data = {
                    'content_type_id': context['person'].content_type_id,
                    'object_pk': context['person'].id,
                    'user_id': self.request.user.id
                })

                if context['person'] in self.request.user.get_profile().monitored_objects:
                    context['is_user_monitoring'] = True
        except ObjectDoesNotExist:
            context['is_user_monitoring'] = False
        return context
