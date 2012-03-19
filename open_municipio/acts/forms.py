from django import forms

from taggit.forms import TagField

class TagAddForm(forms.Form):
    tags = TagField()

