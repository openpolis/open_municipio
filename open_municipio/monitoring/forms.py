from django import forms
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from open_municipio.monitoring.models import Monitoring

class MonitoringForm(forms.Form):
    """
    A form to start or stop monitoring an object.
    
    It contains three hidden fields, that must take value when the form is created.
    """
        
    user_id = forms.IntegerField(widget=forms.HiddenInput)
    content_type_id = forms.IntegerField(widget=forms.HiddenInput)
    object_pk = forms.IntegerField(widget=forms.HiddenInput)
    
    def save(self):
        """creates a new instance of monitoring from form's data and returns it"""
        monitoring = Monitoring(
            content_type_id=self.cleaned_data['content_type_id'],
            object_pk=self.cleaned_data['object_pk'],
            user_id=self.cleaned_data['user_id']
        )
        monitoring.save()
        return monitoring
        
    def remove(self):
        """
            remove monitoring instance, as specified in form's data
            returns False if object was not found
        """
        try:
            monitoring = Monitoring.objects.get(
                content_type=ContentType.objects.get(pk=self.cleaned_data['content_type_id']),
                object_pk=self.cleaned_data['object_pk'],
                user=User.objects.get(pk=self.cleaned_data['user_id'])
            )
            monitoring.delete()
            return True
        except ObjectDoesNotExist:
            return False