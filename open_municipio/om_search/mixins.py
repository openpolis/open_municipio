"""
These mixins allow to use custom range facets on different fields.
Ranges must be defined in the extending class.
The extending class, must also extend a View (possibly a SearchView) class,
in order to make the self.request work.
"""

class FacetRangeDateIntervalsMixin:
    DATE_INTERVALS_RANGES = {}

    def _get_custom_facet_queries_date(self, date_field='pub_date'):
        """

        """
        selected_facets = self.request.GET.getlist('selected_facets') + \
            self.request.GET.getlist('f')

        facet_counts_queries = self.results.facet_counts().get('queries', {})

        facets = {'is_selected': False, 'ranges': []}
        for r in sorted(self.DATE_INTERVALS_RANGES.keys()):
            if "%s:%s" % (date_field, self.DATE_INTERVALS_RANGES[r]['qrange']) in facet_counts_queries:
                facets['ranges'].append({
                    'key': "%s:%s" % (date_field, self.DATE_INTERVALS_RANGES[r]['qrange']),
                    'count': facet_counts_queries["%s:%s" % (date_field, self.DATE_INTERVALS_RANGES[r]['qrange'])],
                    'label': self.DATE_INTERVALS_RANGES[r]['r_label']
                })
                if "%s:%s" % (date_field, self.DATE_INTERVALS_RANGES[r]['qrange']) in selected_facets:
                    facets['is_selected'] = True

        return facets

    def add_date_interval_extended_selected_facets(self, extended_selected_facets, date_field='pub_date'):
        for selected_facet in extended_selected_facets:
            if selected_facet['field'] == date_field:
                for range in self.DATE_INTERVALS_RANGES.keys():
                    if selected_facet['label'] == self.DATE_INTERVALS_RANGES[range]['qrange']:
                        selected_facet['r_label'] = self.DATE_INTERVALS_RANGES[range]['r_label']
        return extended_selected_facets

"""
class TerritorioMixin:
    def add_territorio_extended_selected_facets(self, extended_selected_facets):
        for selected_facet in extended_selected_facets:
            territorio_com = self.request.GET.get('territorio_com', 0)
            territorio_prov = self.request.GET.get('territorio_prov', 0)
            territorio_reg = self.request.GET.get('territorio_reg', 0)
            if territorio_com != '0':
                selected_facet['url'] += "&territorio_com={0}".format(territorio_com)
            if territorio_prov != '0':
                selected_facet['url'] += "&territorio_prov={0}".format(territorio_prov)
                #if territorio_reg != '0':
            selected_facet['url'] += "&territorio_reg={0}".format(territorio_reg)


        return extended_selected_facets
"""