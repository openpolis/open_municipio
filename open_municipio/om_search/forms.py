from django import forms
from haystack.forms import SearchForm
import sys

class RangeFacetedSearchForm(SearchForm):
    person = forms.CharField(required=False)
    recipient = forms.CharField(required=False)
    category = forms.CharField(required=False)
    tag = forms.CharField(required=False)
    location = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        self.selected_facets = kwargs.pop("selected_facets", [])
        self.act_url = kwargs.pop("act_url", [])
        super(RangeFacetedSearchForm, self).__init__(*args, **kwargs)

    def no_query_found(self):
        """
        Determines the behavior when no query was found.
        """
        return self.searchqueryset.all()

    def search(self):
        sqs = super(RangeFacetedSearchForm, self).search()

        # filter for votations in single act
        if self.act_url:
            sqs = sqs.filter(act_url=self.act_url)

        # We need to process each facet to ensure that the field name and the
        # value are quoted correctly and separately:
        for facet in self.selected_facets:
            if ":" not in facet:
                continue

            field, value = facet.split(":", 1)

            if value:
                if  value[0]=='[' and value[-1]==']':
                    sqs = sqs.narrow(u'%s:%s' % (field, value))
                else:
                    sqs = sqs.narrow(u'%s:"%s"' % (field, sqs.query.clean(value)))

        # aggiunge filtro person, se presente
        if self.is_valid() and self.cleaned_data.get('person'):
            sqs = sqs.filter_and(person=self.cleaned_data['person'])
        if self.is_valid() and self.cleaned_data.get('recipient'):
            sqs = sqs.filter_and(recipient=self.cleaned_data['recipient'])

        # aggiunge filtri per category, tag o location, se presenti
        if self.is_valid() and self.cleaned_data.get('category'):
            sqs = sqs.filter_and(categories_with_urls=self.cleaned_data['category'])
        if self.is_valid() and self.cleaned_data.get('tag'):
            sqs = sqs.filter_and(tags_with_urls=self.cleaned_data['tag'])
        if self.is_valid() and self.cleaned_data.get('location'):
            sqs = sqs.filter_and(locations_with_urls=self.cleaned_data['location'])

        return sqs
