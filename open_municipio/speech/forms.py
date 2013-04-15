from django import forms
from django.contrib import admin

from open_municipio.fields import SplitTimeField
from open_municipio.widgets import SplitTimeWidget

class SpeechAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SpeechAdminForm, self).__init__(*args, **kwargs)
        self.fields['begin_time'] = SplitTimeField(widget = SplitTimeWidget)
