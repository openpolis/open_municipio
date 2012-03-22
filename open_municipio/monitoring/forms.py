from django import forms
from django.forms import ModelForm

from open_municipio.monitoring.models import Monitoring

class MonitoringForm(ModelForm):
    """
    A form to start or stop monitoring an object.
    
    It contains three hidden fields, that must take value when the form is created.
    """
    content_type_id = forms.IntegerField(widget=forms.HiddenInput)
    object_pk = forms.IntegerField(widget=forms.HiddenInput)

    class Meta:
        model = Monitoring
        fields = ('content_type_id', 'object_pk')

