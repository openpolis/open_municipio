from django import forms
from django.forms import ModelForm

from open_municipio.monitoring.models import Monitoring

class MonitoringForm(ModelForm):
    """
    A form to start or stop monitoring an object.
    
    It contains two hidden fields, that must take value when the form is created.
    """
    # FIXME: should be a ``ModelChoiceField``;
    # this way, further validation would be performed
    content_type_id = forms.IntegerField(widget=forms.HiddenInput)
    # FIXME: should be a ``ModelChoiceField``;
    # this way, further validation would be performed
    object_pk = forms.IntegerField(widget=forms.HiddenInput)

    class Meta:
        model = Monitoring
        fields = ('content_type_id', 'object_pk')

