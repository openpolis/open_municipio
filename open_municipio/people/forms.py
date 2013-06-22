from django import forms
from open_municipio.widgets import SortWidget

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