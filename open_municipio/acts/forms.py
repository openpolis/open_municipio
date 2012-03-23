from django import forms
from django.forms.models import ModelForm

from taggit.forms import TagField
from open_municipio.acts.models import Act


class ActDescriptionForm(ModelForm):
    description = forms.Textarea()
    id = forms.IntegerField(widget=forms.HiddenInput)

    class Meta:
        model = Act
        fields = ('id', 'description',)

class TagAddForm(forms.Form):
    tags = TagField()

