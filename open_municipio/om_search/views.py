from haystack.views import SearchView
from forms import RangeFacetedSearchForm

class ExtendedFacetedSearchView(SearchView):
    """
    Extends the SearchView class, allowing building filters and breadcrumbs
    for faceted navigation
    """
    __name__ = 'ExtendedFacetedSearchView'

    def __init__(self, *args, **kwargs):
        # Needed to switch out the default form class.
        if kwargs.get('form_class') is None:
            kwargs['form_class'] = RangeFacetedSearchForm

        super(ExtendedFacetedSearchView, self).__init__(*args, **kwargs)

    def build_form(self, form_kwargs=None):
        if form_kwargs is None:
            form_kwargs = {}

        # This way the form can always receive a list containing zero or more
        # facet expressions:
        form_kwargs['selected_facets'] = self.request.GET.getlist('selected_facets')

        return super(ExtendedFacetedSearchView, self).build_form(form_kwargs)

    def _get_extended_facets_fields(self):
        """
        Returns the facets fields information along with a *is_facet_selected*
        field, that allows easy filtering of the selected facets in the
        navigation filters
        """
        selected_facets = self.request.GET.getlist('selected_facets')
        facet_counts_fields = self.results.facet_counts().get('fields', {})

        facets = {'fields': {}, 'dates': {}, 'queries': {}}
        for field, counts in facet_counts_fields.iteritems():
            facets['fields'][field] = {'is_field_selected': False, 'counts': []}
            for count in counts:
                if count > 0:
                    facet = list(count)
                    is_facet_selected = "%s:%s" % (field, facet[0]) in selected_facets
                    facet.append(is_facet_selected)
                    facets['fields'][field]['counts'].append(facet)
                    if is_facet_selected:
                        facets['fields'][field]['is_field_selected'] = True

        return facets

    def _get_extended_selected_facets(self):
        """
        Returns the selected_facets list, in an extended dictionary,
        in order to make it easy to write faceted navigation breadcrumbs
        with *unselect* urls
        unselecting a breadcrumb remove all following selections
        """

        ## original selected facets list
        selected_facets = self.request.GET.getlist('selected_facets')

        extended_selected_facets = []
        for f in selected_facets:
            ## start building unselection url
            url = "?q=%s" % self.query
            for cf in selected_facets:
                if cf != f:
                    url += "&amp;selected_facets=%s" % cf
            field, x, label = f.partition(":")

            r_label = label

            sf = {'field': field, 'label': label, 'r_label': r_label, 'url': url}
            extended_selected_facets.append(sf)

        return extended_selected_facets

    def _get_sorting_fields(self):
        """
        Returns the sorting_fields list, in an extended dictionary,
        in order to make it easy to write field sorting
        """

        ## original sorting facets list
        sorting_fields = self.request.GET.getlist('order_by')

        extended_sorting_fields = {}

        for f in sorting_fields:

            base_dict = self.request.GET.copy()
            base_dict.pop('order_by')
            base_dict.setlist('order_by', [_f for _f in sorting_fields if _f != f])
            is_desc = f.startswith('-')
            field_name = f[1:] if is_desc else f
            extended_sorting_fields[field_name] = {
                'base_url': '?' + base_dict.urlencode(),
                'desc': is_desc,
                'asc': not is_desc,
                'sorting': 'desc' if is_desc else 'asc'
            }

        return extended_sorting_fields

    def _get_sorting_default(self):
        """
        Returns the sorting default parameter, in an extended dictionary,
        in order to make it easy to write default sorting
        """

        ## original sorting facets list
        sorting_fields = self.request.GET.getlist('order_by')

        base_dict = self.request.GET.copy()

        try:
            base_dict.pop('order_by')
        except KeyError:
            pass

        extended_sorting_default = {
            'base_url': '?' + base_dict.urlencode(),
        }

        return extended_sorting_default


    def extra_context(self):
        """

        Builds extra context, to build facets filters and breadcrumbs

        """
        extra = super(ExtendedFacetedSearchView, self).extra_context()
        extra['n_results'] = len(self.results)
        extra['request'] = self.request
        extra['selected_facets'] = self._get_extended_selected_facets()
        extra['facets'] = self._get_extended_facets_fields()
        extra['order_by'] = self._get_sorting_fields()
        extra['order_by_default'] = self._get_sorting_default()

        # make get array as mutable QueryDict
        params = self.request.GET.copy()
        if 'q' not in params:
            params.update({'q': ''})
        if 'page' in params:
            params.pop('page')
        extra['params'] = params

        return extra

