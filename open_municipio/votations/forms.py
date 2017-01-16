from django import forms
from haystack.forms import SearchForm
import sys
from open_municipio.om_search.forms import RangeFacetedSearchForm

class VotationsSearchForm(RangeFacetedSearchForm):
    charge_present = forms.IntegerField(required=False)
    charge_absent = forms.IntegerField(required=False)
    charge_rebel = forms.IntegerField(required=False)

    def __init__(self, *args, **kwargs):
        super(VotationsSearchForm, self).__init__(*args, **kwargs)

    def search(self):
        sqs = super(VotationsSearchForm, self).search()

        # add filters for charges
        if self.is_valid():
            if self.cleaned_data.get('charge_present'):
                sqs = sqs.filter_and(charge_present=self.cleaned_data['charge_present'])
            if self.cleaned_data.get('charge_absent'):
                sqs = sqs.filter_and(charge_absent=self.cleaned_data['charge_absent'])
            if self.cleaned_data.get('charge_rebel'):
                sqs = sqs.filter_and(charge_rebel=self.cleaned_data['charge_rebel'])

        return sqs
