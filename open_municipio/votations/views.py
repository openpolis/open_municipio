from django.views.generic import DetailView
from django.core.urlresolvers import reverse

from open_municipio.votations.models import Votation

from open_municipio.acts.models import Agenda, Deliberation, Interrogation, Interpellation, Motion, Act

from open_municipio.om_search.forms import RangeFacetedSearchForm
from open_municipio.om_search.views import ExtendedFacetedSearchView



class VotationSearchView(ExtendedFacetedSearchView):
    """

    This view allows faceted search and navigation of the votations.

    It extends an extended version of the basic FacetedSearchView,
    and can be customized

    """
    __name__ = 'VotationSearchView'

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

