from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import DetailView
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from open_municipio.om_search.mixins import FacetRangeDateIntervalsMixin
from open_municipio.people.models import Person

from open_municipio.votations.models import Votation

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

    DATE_INTERVALS_RANGES = {
        '2012':  {'qrange': '[2012-01-01T00:00:00Z TO 2013-01-01T00:00:00Z]', 'r_label': '2012'},
        '2011':  {'qrange': '[2011-01-01T00:00:00Z TO 2012-01-01T00:00:00Z]', 'r_label': '2011'},
        '2010':  {'qrange': '[2010-01-01T00:00:00Z TO 2011-01-01T00:00:00Z]', 'r_label': '2010'},
        '2009':  {'qrange': '[2009-01-01T00:00:00Z TO 2010-01-01T00:00:00Z]', 'r_label': '2009'},
        '2008':  {'qrange': '[2008-01-01T00:00:00Z TO 2009-01-01T00:00:00Z]', 'r_label': '2008'},
    }


    def __init__(self, *args, **kwargs):
        # Needed to switch out the default form class.
        if kwargs.get('form_class') is None:
            kwargs['form_class'] = RangeFacetedSearchForm

        super(VotationSearchView, self).__init__(*args, **kwargs)

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
        extended_selected_facets = self.add_date_interval_extended_selected_facets(extended_selected_facets)

        return extended_selected_facets

    def extra_context(self):
        """
        Add extra content here, when needed
        """
        extra = super(VotationSearchView, self).extra_context()
        extra['act_votations'] = False
        extra['base_url'] = reverse('om_votation_search') + '?' + extra['params'].urlencode()

        if self.request.GET.get("act_url"):
            act_id = int(self.request.GET.get('act_url').split("/")[-2])
            extra['act_votations'] = True
            extra['act'] = Act.objects.get(pk=act_id).downcast()

        person_slug = self.request.GET.get('person', None)
        if person_slug:
            try:
                extra['person'] = Person.objects.get(slug=person_slug)
            except ObjectDoesNotExist:
                pass


        paginator = Paginator(self.results, settings.HAYSTACK_SEARCH_RESULTS_PER_PAGE)
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
        context['votation_difference'] = abs(votation.n_yes - votation.n_no)
        return context

