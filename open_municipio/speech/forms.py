from django import forms
from django.contrib import admin

from open_municipio.speech.widgets import SplitTimeField, SplitTimeWidget

class SpeechAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SpeechAdminForm, self).__init__(*args, **kwargs)
        self.fields['begin_time'] = SplitTimeField(widget = SplitTimeWidget)
