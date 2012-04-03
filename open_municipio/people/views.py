from django.template.context import RequestContext
from os import sys

from django.http import Http404, HttpResponseRedirect
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

        mayor = municipality.mayor.as_charge
        president = municipality.council.members.get(
            charge_type=InstitutionCharge.COUNCIL_PRES_CHARGE)
        vice_president = municipality.council.members.get(
            charge_type=InstitutionCharge.COUNCIL_VICE_CHARGE)
        groups = municipality.council.groups
        committees = municipality.committees.as_institution
        latest_acts = Act.objects.filter(
            emitting_institution__institution_type=Institution.COUNCIL
            ).order_by('-presentation_date')[:3]
        events = Event.future.filter(
            institution__institution_type=Institution.COUNCIL
            )
        num_acts = dict()
        act_types = [
            Deliberation, Motion, Interrogation, Interpellation, Agenda
            ]
        for act_type in act_types:
            num_acts[act_type.__name__.lower()] = act_type.objects.filter(
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

        citygov = municipality.gov
        latest_acts = Act.objects.filter(
            emitting_institution__institution_type=Institution.CITY_GOVERNMENT
            ).order_by('-presentation_date')[:3]
        events = Event.future.filter(
            institution__institution_type=Institution.CITY_GOVERNMENT
            )
        num_acts = dict()
        act_types = [
            Deliberation, Motion, Interrogation, Interpellation, Agenda
            ]
        for act_type in act_types:
            num_acts[act_type.__name__.lower()] = act_type.objects.filter(
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


class CommitteeDetailView(DetailView):
    """
    Renders the Committee page
    """
    model = Institution
    template_name = 'people/institution_committee.html'
    context_object_name = "committee"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CommitteeDetailView, self).get_context_data(**kwargs)

        # Are we given a real Committee institution as input? If no,
        # raise 404 exception.
        if self.object.institution_type != Institution.COMMITTEE:
            raise Http404

        committee_list = Institution.objects.filter(institution_type=Institution.COMMITTEE)

        # Under the hood, we make use of a custom manager here, so
        # that *only* current institution charges are retrieved.
        members = InstitutionCharge.objects.filter(
            institution=self.object
            ).filter(
            charge_type=InstitutionCharge.COMMITTEE_MEMBER_CHARGE
            )

        # FIXME: do we really want this? Is that necessary? Is there
        # any other *smarter* way to do that?
        for member in members:
            try:
                counselor_charge = member.person.current_institution_charges.filter(
                    charge_type=InstitutionCharge.COUNSELOR_CHARGE
                    )[0]
            except IndexError:
                continue
            member.counselor_group = counselor_charge.council_group
            
        events = Event.future.filter(institution=self.object)

        extra_context = {
            'committee_list': committee_list,
            'members': members,
            'events': events,
            }

        # Update context with extra values we need
        context.update(extra_context)
        return context


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


def person_list(request):
    return render_to_response('people/person_list.html',{
        'municipality': municipality
    },context_instance=RequestContext(request) )


def show_mayor(request):
    return HttpResponseRedirect( municipality.mayor.as_charge.person.get_absolute_url() )
