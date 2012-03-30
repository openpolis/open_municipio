from haystack.views import SearchView
from open_municipio.om_search.forms import RangeFacetedSearchForm

class ExtendedFacetedSearchView(SearchView):
    """
    Extends the SearchView class, allowing building filters and breadcrumbs
    for faceted navigation
    """
    __name__ = 'ExtendedFacetedSearchView'

    ## simplified date-ranges definitions
    THREEDAYS = '[NOW/DAY-3DAYS TO NOW/DAY]'
    ONEMONTH  = '[NOW/DAY-30DAYS TO NOW/DAY]'
    ONEYEAR   = '[NOW/DAY-365DAYS TO NOW/DAY]'

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
        form_kwargs['selected_facets'] = self.request.GET.getlist("selected_facets")

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
            field, _, label = f.partition(":")

            # TODO: use an associative array
            if field == 'pub_date':
                if label == self.THREEDAYS:
                    label = 'ultimi 3 giorni'
                elif label == self.ONEMONTH:
                    label = 'ultimo mese'
                else:
                    raise Exception

            sf = {'field': field, 'label': label, 'url': url}
            extended_selected_facets.append(sf)

        return extended_selected_facets

    def _get_custom_facet_queries_pubdate(self):
        """

        """
        selected_facets = self.request.GET.getlist('selected_facets')
        facet_counts_queries = self.results.facet_counts().get('queries', {})

        facets = {'is_selected': False}
        if "pub_date:%s" % self.THREEDAYS in facet_counts_queries:
            facets['threedays'] = {
                'key': "pub_date:%s" % self.THREEDAYS,
                'count': facet_counts_queries["pub_date:%s" % self.THREEDAYS]
            }
            if (facets['threedays']['key'] in selected_facets):
                facets['is_selected'] = True

        if "pub_date:%s" % self.ONEMONTH in facet_counts_queries:
            facets['onemonth'] = {
                'key': "pub_date:%s" % self.ONEMONTH,
                'count': facet_counts_queries["pub_date:%s" % self.ONEMONTH]
            }
            if (facets['onemonth']['key'] in selected_facets):
                facets['is_selected'] = True

        return facets


    def extra_context(self):
        """

        Builds extra context, to build facets filters and breadcrumbs

        """
        extra = super(ExtendedFacetedSearchView, self).extra_context()
        extra['n_results'] = len(self.results)
        extra['request'] = self.request
        extra['selected_facets'] = self._get_extended_selected_facets()
        extra['facets'] = self._get_extended_facets_fields()
        extra['facet_queries_pubdate'] = self._get_custom_facet_queries_pubdate()

        # make get array as mutable QueryDict
        params = self.request.GET.copy()
        if 'q' not in params:
            params.update({'q': ''})
        if 'page' in params:
            params.pop('page')

        from django.core.urlresolvers import reverse
        extra['base_url'] = reverse('om_act_search') + '?' + params.urlencode()

        return extra

