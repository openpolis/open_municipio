from datetime import datetime
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import DetailView
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from open_municipio.om_search.mixins import FacetRangeDateIntervalsMixin
from open_municipio.people.models import Person, InstitutionCharge
from django.utils.translation import ugettext_lazy as _

from haystack.query import SearchQuerySet

from open_municipio.votations.models import Votation, ChargeVote

from open_municipio.acts.models import Agenda, Deliberation, Interrogation, Interpellation, Motion, Act

from open_municipio.om_search.forms import RangeFacetedSearchForm
from open_municipio.om_search.views import ExtendedFacetedSearchView



class VotationSearchView(ExtendedFacetedSearchView, FacetRangeDateIntervalsMixin):
    """

    This view allows faceted search and navigation of the votations.

    It extends an extended version of the basic FacetedSearchView,
    and can be customized

    """
    __name__ = 'VotationSearchView'

    FACETS_SORTED = ['act_type', 'is_key', 'is_secret', 'organ', 'votation_outcome',
        'n_presents_range', 'n_rebels_range', 'n_variance', 'votation_date', 'month']

    FACETS_LABELS = {
        'act_type': _('Related act type'),
        'is_key': _('Is key'),
        'is_secret': _('Is secret'),
        'organ': _('Organ'),
        'votation_outcome': _('Outcome'),
        'n_presents_range': _('Presents'),
        'n_rebels_range': _('Rebels'),
        'n_variance': _('Votation variance'),
        'votation_date': _('Sitting year'),
        'month': _('Sitting month')
    }
    DATE_INTERVALS_RANGES = { }

    def __init__(self, *args, **kwargs):

        # dynamically compute date ranges for faceted search
        curr_year = datetime.today().year
        for curr_year in xrange(settings.OM_START_YEAR, curr_year + 1):
            date_range = self._build_date_range(curr_year)
            self.DATE_INTERVALS_RANGES[curr_year] = date_range
    
        sqs = SearchQuerySet().filter(django_ct='votations.votation').\
            facet('act_type').facet('is_key').facet('is_secret').facet('organ').\
            facet('n_presents_range').facet('n_rebels_range').\
            facet('n_variance').facet('votation_outcome').facet('month')

        for (year, range) in self.DATE_INTERVALS_RANGES.items():
            sqs = sqs.query_facet('votation_date', range['qrange'])

        sqs = sqs.order_by('-votation_date').highlight()
        kwargs['searchqueryset'] = sqs

        # Needed to switch out the default form class.
        if kwargs.get('form_class') is None:
            kwargs['form_class'] = RangeFacetedSearchForm

        super(VotationSearchView, self).__init__(*args, **kwargs)

    def _build_date_range(self, curr_year):
        return { 'qrange': '[%s-01-01T00:00:00Z TO %s-12-31T00:00:00Z]' % \
                (curr_year, curr_year), 'r_label': curr_year }

    def build_page(self):
        self.results_per_page = int(self.request.GET.get('results_per_page', settings.HAYSTACK_SEARCH_RESULTS_PER_PAGE))
        return super(VotationSearchView, self).build_page()

    def build_form(self, form_kwargs=None):
        if form_kwargs is None:
            form_kwargs = {}

        # This way the form can always receive a list containing zero or more
        # facet expressions:
        form_kwargs['act_url'] = self.request.GET.get("act_url")

        return super(VotationSearchView, self).build_form(form_kwargs)

    def _get_extended_selected_facets(self):
        """
        modifies the extended_selected_facets, adding correct labels for this view
        works directly on the extended_selected_facets dictionary
        """
        extended_selected_facets = super(VotationSearchView, self)._get_extended_selected_facets()

        # this comes from the Mixins
        extended_selected_facets = self.add_date_interval_extended_selected_facets(extended_selected_facets, 'votation_date')

        return extended_selected_facets

    def extra_context(self):
        """
        Add extra content here, when needed
        """
        extra = super(VotationSearchView, self).extra_context()
        extra['act_votations'] = False
        extra['base_url'] = reverse('om_votation_search') + '?' + extra['params'].urlencode()

        if self.request.GET.get("act_url"):
            act_id_or_slug = self.request.GET.get('act_url').split("/")[-2]

            act = None
            if act_id_or_slug.isdigit():
                act = Act.objects.get(pk=act_id_or_slug)
            else:
                act = Act.objects.get(slug=act_id_or_slug)

            extra['act_votations'] = True
            extra['act'] = act.downcast()

        person_slug = self.request.GET.get('person', None)
        if person_slug:
            try:
                extra['person'] = Person.objects.get(slug=person_slug)
            except ObjectDoesNotExist:
                pass

        # get data about custom date range facets
        extra['facet_queries_date'] = self._get_custom_facet_queries_date('votation_date')

        extra['facets_sorted'] = self.FACETS_SORTED
        extra['facets_labels'] = self.FACETS_LABELS

        paginator = Paginator(self.results, self.results_per_page)
        page = self.request.GET.get('page', 1)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            page_obj = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            page_obj = paginator.page(paginator.num_pages)

        extra['paginator'] = paginator
        extra['page_obj'] = page_obj

        return extra


class VotationDetailView(DetailView):
    """
    Renders a Votation page
    """
    model = Votation
    template_name = 'votations/votation_detail.html'
    context_object_name = 'votation'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(VotationDetailView, self).get_context_data(**kwargs)

        # get last two calendar events

        votation = self.get_object()
        voters = ChargeVote.objects.filter(votation=votation).order_by('charge__person__last_name', 'charge__person__first_name')

        names_yes = self._get_names(voters, ["YES",])
        names_no = self._get_names(voters, ["NO",])
        names_abst = self._get_names(voters, ["ABSTAINED","PRES",])
        n_pres_not_voting = abs(votation.n_presents - votation.n_partecipants)

        context['n_absents'] = votation.chargevote_set.filter(vote=ChargeVote.VOTES.absent).count()
        context['n_pres_not_voting'] = n_pres_not_voting
        context['n_abst'] = votation.n_abst + n_pres_not_voting
        context['votation_difference'] = abs(votation.n_yes - votation.n_no)
        context['names_yes'] = names_yes
        context['names_no'] = names_no
        context['names_abst'] = names_abst

        return context

    def _get_names(self, voters, vote_list):
        
        matching = filter(lambda v: v.vote in vote_list, voters)

        return ", ".join(map(self._get_label, matching))
       

    def _get_label(self, cv):

        assert isinstance(cv, ChargeVote)

        name = cv.charge.person.first_name
        surname = cv.charge.person.last_name
        group = ""
        try:
            group = " (%s)" % (cv.charge.current_groupcharge.group.acronym,)
        except: 
            pass

        label = "%s. %s%s" % (name[0], surname, group)

        return label
