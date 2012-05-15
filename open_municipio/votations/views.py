from django.views.generic import DetailView
from django.core.urlresolvers import reverse

from open_municipio.votations.models import Votation

from open_municipio.acts.models import Agenda, Deliberation, Interrogation, Interpellation, Motion

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
        form_kwargs['selected_facets'] = self.request.GET.getlist("selected_facets")

        form_kwargs['act_url'] = self.request.GET.get("act_url")

        return super(VotationSearchView, self).build_form(form_kwargs)

    def extra_context(self):
        """
        Add extra content here, when needed
        """
        extra = super(VotationSearchView, self).extra_context()
        extra['base_url'] = reverse('om_votation_search') + '?' + extra['params'].urlencode()
        return extra


class VotationDetailView(DetailView):
    """
    Renders a Votation page
    """
    model = Votation
    template_name = 'votations/votation_detail.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(VotationDetailView, self).get_context_data(**kwargs)

        votation = self.object

        if votation.act:
            # So we have an act. What kind of act, specifically? (FIXME: I
            # don't like the way act types are hardcoded here with their
            # Italian names.)
            if votation.act.downcast().__class__() == Agenda().__class__():
                act_type = "Ordine del Giorno"
            elif votation.act.downcast().__class__() == Deliberation().__class__():
                act_type = "Delibera"
            elif votation.act.downcast().__class__() == Interpellation().__class__():
                act_type = "Interpellanza"
            elif votation.act.downcast().__class__() == Interrogation().__class__():
                act_type = "Interrogazione"
            elif votation.act.downcast().__class__() == Motion().__class__():
                act_type = "Mozione"

            votation.act_type = act_type

        extra_context = {
            'votation': votation,
            }

        # Update context with extra values we need
        context.update(extra_context)
        return context