from django import forms

from open_municipio.acts.models import Act, Transition

class ActTitleForm(forms.ModelForm):
    class Meta:
        model = Act
        fields = ('id', 'title',)


class ActDescriptionForm(forms.ModelForm):
    class Meta:
        model = Act
        fields = ('id', 'description',)


class ActTransitionForm(forms.ModelForm):
    """
    A form to change status of act
    """
    def save(self, commit=True):
        instance = super(forms.ModelForm, self).save(commit=False)
        instance.act = instance.act.downcast()
        if commit:
            instance.save()
        return instance

    class Meta:
        model = Transition
        fields = ('transition_date', 'note', 'final_status', 'act')
        widgets = {
            'act': forms.HiddenInput(),
            'final_status': forms.HiddenInput(),
            'transition_date': forms.DateTimeInput(attrs={'class':'datepicker'})
        }


class ActFinalTransitionForm(ActTransitionForm):
    """
    Extends ActTransitionForm to provide a vote selection
    """

    class Meta(ActTransitionForm.Meta):
        fields = ('transition_date', 'note', 'final_status', 'act', 'votation')
        widgets = {
            'act': forms.HiddenInput(),
            'final_status': forms.Select(choices=[]),
            'transition_date': forms.DateTimeInput(attrs={'class':'datepicker'})
        }