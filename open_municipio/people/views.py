from django.http import Http404
from django.views.generic import TemplateView, DetailView, ListView, RedirectView
from django.core.exceptions import ObjectDoesNotExist

from open_municipio.people.models import Institution, InstitutionCharge, Person, municipality
from open_municipio.monitoring.forms import MonitoringForm
from open_municipio.acts.models import Act, Deliberation, Interrogation, Interpellation, Motion, Agenda
from open_municipio.events.models import Event

from os import sys



class InstitutionListView(ListView):
    model = Institution
    template_name = 'people/institution_list.html'
    
    
class MayorDetailView(RedirectView):
    def get_redirect_url(self, **kwargs):
        return municipality.mayor.as_charge.person.get_absolute_url()


class CouncilDetailView(TemplateView):
    """
    Renders the Council page
    """
    template_name = 'people/institution_council.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CouncilDetailView, self).get_context_data(**kwargs)

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


class PoliticianDetailView(DetailView):
    model = Person
    context_object_name = 'person'
    template_name='people/politician_detail.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(PoliticianDetailView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the institutions
        context['institution_list'] = Institution.objects.all()

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