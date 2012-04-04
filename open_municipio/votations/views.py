from open_municipio.om_search.forms import RangeFacetedSearchForm
from open_municipio.om_search.views import ExtendedFacetedSearchView

from django.core.urlresolvers import reverse

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
        form_kwargs['selected_facets'] = self.request.GET.getlist("selected_facets")

        return super(VotationSearchView, self).build_form(form_kwargs)

    def extra_context(self):
        """
        Add extra content here, when needed
        """
        extra = super(VotationSearchView, self).extra_context()
        extra['base_url'] = reverse('om_votation_search') + '?' + extra['params'].urlencode()
        return extra


