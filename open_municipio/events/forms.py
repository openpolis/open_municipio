from django import forms
from haystack.forms import SearchForm
import sys
from open_municipio.om_search.forms import RangeFacetedSearchForm

class EventsSearchForm(RangeFacetedSearchForm):

    def __init__(self, *args, **kwargs):
        super(EventsSearchForm, self).__init__(*args, **kwargs)

    def search(self):
        sqs = super(EventsSearchForm, self).search()

        # default sorting
        if (self.is_valid() and not self.cleaned_data.get('order_by')) or not self.is_valid():
            sqs = sqs.order_by('-date')

        return sqs
