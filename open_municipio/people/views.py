from django.http import Http404, HttpResponseRedirect
from django.views.generic import TemplateView, DetailView, ListView, RedirectView
from django.core.exceptions import ObjectDoesNotExist

from open_municipio.people.models import Institution, InstitutionCharge, Person, municipality, InstitutionResponsability, Resource, GroupCharge
from open_municipio.monitoring.forms import MonitoringForm
from open_municipio.acts.models import Act, Deliberation, Interrogation, Interpellation, Motion, Agenda
from open_municipio.events.models import Event
from open_municipio.votations.models import ChargeVote

from operator import attrgetter
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
        president = municipality.council.president
        vicepresidents = municipality.council.vicepresidents
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
            'vicepresidents': vicepresidents,
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

        mayor = municipality.mayor.as_charge
        firstdeputy = municipality.gov.firstdeputy.charge
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
            'mayor': mayor,
            'firstdeputy': firstdeputy,
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

        committee_list = municipality.committees.as_institution()

        # fetch charges and add group
        president = self.object.president
        if president:
            president.group = InstitutionCharge.objects.current().select_related().\
                                  get(pk=president.charge.original_charge_id).council_group
        vicepresidents = self.object.vicepresidents
        for vp in vicepresidents:
            if vp:
                vp.group = InstitutionCharge.objects.current().select_related().\
                    get(pk=vp.charge.original_charge_id).council_group
        members = self.object.members.order_by('person__last_name')
        for m in members:
            m.group = InstitutionCharge.objects.current().select_related().\
                get(pk=m.original_charge_id).council_group


        resources = dict(
            (r['resource_type'], {'value': r['value'], 'description': r['description']})
                for r in self.object.resources.values('resource_type', 'value', 'description')
        )

        events = Event.future.filter(institution=self.object)

        extra_context = {
            'committees': committee_list,
            'members': members,
            'president': president,
            'resources': resources,
            'vice_presidents': vicepresidents,
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

        context['resources'] = dict(
            (r['resource_type'], {'value': r['value'], 'description': r['description']})
            for r in self.object.resources.values('resource_type', 'value', 'description')
        )
        context['current_charges'] = self.object.get_current_institution_charges().exclude(
            institutionresponsability__charge_type__in=(
                InstitutionResponsability.CHARGE_TYPES.mayor,
            ),
            institutionresponsability__end_date__isnull=True
        )
        context['get_current_committee_charges'] = self.object.get_current_committee_charges()


        context['current_groupcharge'] = self.object.current_groupcharge

        historical_groupcharges = self.object.historical_groupcharges
        context['historical_groupcharges'] = historical_groupcharges.order_by('start_date') if historical_groupcharges else None

        # Is politician a counselor? If so, we show present/absent
        # graph
        for charge in context['current_charges']:
            if charge.institution.institution_type == Institution.COUNCIL:
                # Calculate average present/absent for counselors
                percentage_present = 0
                percentage_absent = 0
                n_counselors = len(municipality.council.charges)
                for counselor in municipality.council.charges:
                    n_votations = counselor.n_present_votations \
                        + counselor.n_absent_votations
                    if n_votations > 0:
                        percentage_present += \
                            float(counselor.n_present_votations) / n_votations
                        percentage_absent += \
                            float(counselor.n_absent_votations) / n_votations
                # Empty city council? That can't be the case!
                # n_counselors is supposed to be > 0
                context['percentage_present_votations_average'] = \
                    "%.1f" % (float(percentage_present) / n_counselors * 100)
                context['percentage_absent_votations_average'] = \
                    "%.1f" % (float(percentage_absent) / n_counselors * 100)

                # Calculate present/absent for current counselor
                charge.n_total_votations = 0
                charge.percentage_present_votations = charge.percentage_absent_votations = 0.0

                if charge.n_total_votations > 0:
                    charge.n_total_votations = \
                        charge.n_present_votations + charge.n_absent_votations
                    charge.percentage_present_votations = \
                        "%.1f" % (float(charge.n_present_votations) / \
                                      charge.n_total_votations * 100.00)
                    charge.percentage_absent_votations = \
                        "%.1f" % (float(charge.n_absent_votations) / \
                                      charge.n_total_votations * 100.00)

                self.object.counselor_charge = charge
                break

        # Current politician's charge votes for key votations
        unsorted_current_charge_votes = []
        for charge in context['current_charges']:
            charge_votes = ChargeVote.objects\
                .filter(charge=charge).filter(votation__is_key=True)
            unsorted_current_charge_votes += charge_votes
        # Sort by date 
        current_charge_votes = sorted(
            unsorted_current_charge_votes,
            key=attrgetter('votation.sitting.date'),
            reverse=True
            )
        # Pass data to template
        context['current_charge_votes'] = current_charge_votes

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

        context['person_topics'] = []
        for topics in [y.topics for x in self.object.get_current_institution_charges() for y in x.presented_act_set.all() ]:
            for topic in topics:
                context['person_topics'].append(topic)

        return context


class PoliticianListView(TemplateView):
    """
    Renders the Politicians page
    """
    template_name = 'people/politician_list.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(PoliticianListView, self).get_context_data(**kwargs)

        # municipality access point to internal API
        context['municipality'] = municipality

        # fetch mayor
        context['mayor'] = municipality.mayor.as_charge
        # exclude mayor from gov members
        context['gov_members'] = municipality.gov.charges.exclude(
            institutionresponsability__charge_type__in=(
                InstitutionResponsability.CHARGE_TYPES.mayor,
            ),
            institutionresponsability__end_date__isnull=True
        ).select_related().order_by('person__last_name')
        # exclude mayor from council members
        counselors = context['counselors'] = municipality.council.charges.exclude(
            institutionresponsability__charge_type__in=(
                InstitutionResponsability.CHARGE_TYPES.mayor,
            ),
            institutionresponsability__end_date__isnull=True
        ).select_related().order_by('person__last_name')

        # fetch most or least
        context['most_rebellious'] = counselors.order_by('-n_rebel_votations')[0:3]
        context['least_absent'] = counselors.order_by('n_absent_votations')[0:3]
        context['most_absent'] = counselors.order_by('-n_absent_votations')[0:3]

        # take latest group charge changes
        context['last_group_changes'] = [gc.charge for gc in GroupCharge.objects.filter(
            charge__in= [gc.charge.id for gc in GroupCharge.objects.filter(end_date__isnull=True)]
        ).filter(end_date__isnull=False).order_by('-end_date')[0:3]]

        # TODO: sostituite with real data
        context['most_monitorized'] = context['last_group_changes']

        context['gender_stats'] = {'Uomini': 0, 'Donne': 0}
        context['age_stats'] = context['degree_stats'] = {}
        for charge in municipality.council.members:
            if charge.person.sex == Person.MALE_SEX:
                context['gender_stats']['Uomini'] += 1
            elif charge.person.sex == Person.FEMALE_SEX:
                context['gender_stats']['Donne'] += 1

            if not charge.person.age in context['age_stats']:
                context['age_stats'][charge.person.age] = 0
            context['age_stats'][charge.person.age] += 1

        context['gender_stats'] = context['gender_stats'].items()
        context['age_stats'] = context['age_stats'].items()
        context['degree_stats'] = [('phd',1), ('none',2)]

        return context


def show_mayor(request):
    return HttpResponseRedirect( municipality.mayor.as_charge.person.get_absolute_url() )
