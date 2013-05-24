from django import forms

class SittingItemFormSet(forms.ModelForm):
    class Meta:
        widgets = {
            'seq_order' : forms.TextInput(attrs={'readonly':'readonly',
                'class':'sortable'})
        }
