from django.template.context import RequestContext
from os import sys

from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, DetailView
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, render_to_response

from open_municipio.people.models import Institution, InstitutionCharge, Person, municipality
from open_municipio.monitoring.forms import MonitoringForm
from open_municipio.acts.models import Act, Deliberation, Interrogation, Interpellation, Motion, Agenda
from open_municipio.events.models import Event


class CouncilView(TemplateView):
    """
    Renders the Council page
    """
    template_name = 'people/institution_council.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CouncilView, self).get_context_data(**kwargs)

        mayor = municipality.mayor.as_charge.person
        president = municipality.council.members.get(
            charge_type=InstitutionCharge.COUNCIL_PRES_CHARGE).person
        vice_president = municipality.council.members.get(
            charge_type=InstitutionCharge.COUNCIL_VICE_CHARGE).person
        groups = municipality.council.groups
        committees = municipality.committees.as_institution
        latest_acts = Act.objects.filter(
            emitting_institution__institution_type=Institution.COUNCIL
            ).order_by('-presentation_date')[:3]
        events = Event.objects.filter(
            institution__institution_type=Institution.COUNCIL
            )
        num_acts = dict()
        act_types = [
            Deliberation, Motion, Interrogation, Interpellation, Motion, Agenda
            ]
        for act_type in act_types:
            num_acts[act_type.__name__] = act_type.objects.filter(
                emitting_institution__institution_type=Institution.COUNCIL
                ).count()

        extra_context = {
            'mayor': mayor,
            'president': president,
            'vice_president': vice_president,
            'groups': groups,
            'committees': committees,
            'latest_acts': latest_acts,
            'num_acts': num_acts,
            'events': events,
            }
        
        # Update context with extra values we need
        context.update(extra_context)
        return context


class CityGovernmentView(TemplateView):
    """
    Renders the City Government page
    """
    template_name = 'people/institution_citygov.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CityGovernmentView, self).get_context_data(**kwargs)

        citygov = municipality.gov.members
        latest_acts = Act.objects.filter(
            emitting_institution__institution_type=Institution.CITY_GOVERNMENT
            ).order_by('-presentation_date')[:3]
        events = Event.objects.filter(
            institution__institution_type=Institution.CITY_GOVERNMENT
            )
        num_acts = dict()
        act_types = [
            Deliberation, Motion, Interrogation, Interpellation, Motion, Agenda
            ]
        for act_type in act_types:
            num_acts[act_type.__name__] = act_type.objects.filter(
                emitting_institution__institution_type=Institution.CITY_GOVERNMENT
                ).count()
            
        extra_context = {
            'citygov': citygov,
            'latest_acts': latest_acts,
            'num_acts': num_acts,
            'events': events,
            }

        # Update context with extra values we need
        context.update(extra_context)
        return context


class CommitteeView(DetailView):
    model = Institution
    context_object_name = 'committee'



# TODO: deprecated - use PoliticianDetailView
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


# TODO: deprecated - use PoliticianListView
def person_list(request):
    return render_to_response('people/person_list.html',{
        'municipality': municipality
    },context_instance=RequestContext(request) )


class PoliticianDetailView(DetailView):
    model = Person
    context_object_name = 'person'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(PoliticianDetailView, self).get_context_data(**kwargs)
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

class PoliticianListView(TemplateView):
    """
    Renders the Politicians page
    """
    template_name = 'people/politician_list.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(PoliticianListView, self).get_context_data(**kwargs)

        context['municipality'] = municipality

        all_current = InstitutionCharge.objects.current()

        context['most_rebellious'] = all_current.order_by('-n_rebel_votations')[0:3]
        context['most_present'] = all_current.order_by('-n_present_votations')[0:3]
        context['most_absent'] = all_current.order_by('-n_absent_votations')[0:3]
        return context


def show_mayor(request):
    return HttpResponseRedirect( municipality.mayor.as_charge.person.get_absolute_url() )
