from django import forms

from open_municipio.acts.models import Act

from open_municipio.locations.models import Location


class ActLocationsAddForm(forms.Form):
    """
    A form used to select zero or more locations to be associated with a given act. 
    """
    # the ``Act`` instance being tagged with locations
    act = forms.ModelChoiceField(queryset=Act.objects.all(), widget=forms.HiddenInput)
    # ``Location`` objects being associated to the act 
    locations = forms.ModelMultipleChoiceField(queryset=Location.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)