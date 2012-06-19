from django import forms
from django.forms.models import ModelForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from model_utils import Choices
from registration.forms import RegistrationForm, RegistrationFormUniqueEmail

from open_municipio.users.models import UserProfile


class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user', 'person')


class ProfileSocialRegistrationForm(ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user',)


class UserSocialRegistrationForm(ModelForm):
    class Meta:
        model = User
        fields = ('username',)


class UserRegistrationForm(RegistrationFormUniqueEmail):
    first_name = forms.CharField(max_length=30, required=True, label=_('First Name'))
    last_name = forms.CharField(max_length=30, label=_('Last Name'))
    wants_newsletter = forms.BooleanField(required=False, label=_('Wants newsletter'))
    privacy_level = forms.ChoiceField(choices=UserProfile.PRIVACY_LEVELS, label=_('Privacy level'))
    city = forms.CharField(max_length=128, label=_('Location'))
