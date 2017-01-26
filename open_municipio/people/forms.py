from django import forms
from haystack.forms import SearchForm
import sys
from open_municipio.om_search.forms import RangeFacetedSearchForm
from open_municipio.widgets import SortWidget

class ChargeSearchForm(RangeFacetedSearchForm):

    def __init__(self, *args, **kwargs):
        super(ChargeSearchForm, self).__init__(*args, **kwargs)

    def search(self):
        sqs = super(ChargeSearchForm, self).search()

        # default sorting
        if (self.is_valid() and not self.cleaned_data.get('order_by')) or not self.is_valid():
            sqs = sqs.order_by('last_name')

        return sqs

class GroupSearchForm(RangeFacetedSearchForm):

    def __init__(self, *args, **kwargs):
        super(GroupSearchForm, self).__init__(*args, **kwargs)

    def search(self):
        sqs = super(GroupSearchForm, self).search()

        # default sorting
        if (self.is_valid() and not self.cleaned_data.get('order_by')) or not self.is_valid():
            sqs = sqs.order_by('name')

        return sqs

class SittingItemFormSet(forms.ModelForm):
    class Meta:
        widgets = {
            'seq_order' : SortWidget()
        }

class SpeechInlineForm(forms.ModelForm):
    class Meta:
        widgets = {
            "seq_order" : SortWidget()
        }