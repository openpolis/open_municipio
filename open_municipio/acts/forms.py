from django import forms
from django.forms.widgets import HiddenInput
from taggit.forms import TagField
from django.forms.models import ModelForm
from open_municipio.acts.models import Transition, Deliberation


class TagAddForm(forms.Form):
    tags = TagField()

class ActTransitionForm(ModelForm):
    """
    A form to change status of act
    """
    def save(self, commit=True):
        instance = super(ModelForm, self).save(commit=False)
        instance.act = instance.act.downcast()
        if commit:
            instance.save()
        return instance

    class Meta:
        model = Transition
        fields = ('transition_date', 'note', 'final_status', 'act')
        widgets = {
            'act': HiddenInput(),
            'final_status': HiddenInput()
        }


class ActFinalTransitionForm(ActTransitionForm):
    """
    Extends ActTransitionForm to provide a vote selection
    """

    class Meta(ActTransitionForm.Meta):
        fields = ('transition_date', 'note', 'final_status', 'act', 'votation')
        widgets = {
            'act': HiddenInput(),
            'final_status': forms.Select(choices=[])
        }
