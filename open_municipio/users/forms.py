from django import forms
from django.forms.models import ModelForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from model_utils import Choices
from registration.forms import RegistrationForm, RegistrationFormUniqueEmail

from open_municipio.users.models import UserProfile


"""
``User`` and ``UserProfile`` model forms. A few of them are used in
the ``django-social-auth`` registration process, whenever some extra
data are needed.
"""

# This is just a shortcut
attrs_dict = {'class': 'required'}

class UserRegistrationForm(RegistrationFormUniqueEmail):
    """
    ``User`` and ``UserProfile`` model form for standard (non-social)
    registration.
    """
    first_name = forms.CharField(max_length=30, required=True, label=_('First Name'))
    last_name = forms.CharField(max_length=30, label=_('Last Name'))
    city = forms.CharField(widget=forms.TextInput(attrs=attrs_dict))
    says_is_politician = forms.BooleanField(required=False, label=_('I am a politician'))
    uses_nickname = forms.BooleanField(widget=forms.CheckboxInput(attrs=attrs_dict),
                                       label=_(u'User wants only his nickname to be publicly shown'),
                                       required=False)
    wants_newsletter = forms.BooleanField(required=False, label=_('Wants newsletter'))
    privacy_level = forms.ChoiceField(choices=UserProfile.PRIVACY_LEVELS, label=_('Privacy level'))
    tos = forms.BooleanField(widget=forms.CheckboxInput(attrs=attrs_dict),
                             label=_(u'I have read and agree to the Terms of Service'),
                             error_messages={'required': _("You must agree to the terms to register")})
    pri = forms.BooleanField(widget=forms.CheckboxInput(attrs=attrs_dict),
                             label=_(u'I have read and agree to the Privacy conditions'),
                             error_messages={'required': _("You must agree to the conditions to register")})


class UserSocialRegistrationForm(ModelForm):
    """
    ``User`` model form for social registration: collecting
    some extra data not provided by social networks.
    """
    class Meta:
        model = User
        fields = ('username',)


class ProfileSocialRegistrationForm(ModelForm):
    """
    ``UserProfile`` model form for social registration: collecting
    some extra data not provided by social networks.
    """
    class Meta:
        model = UserProfile
        exclude = ('user', 'person')


class UserProfileForm(ModelForm):
    """
    ``UserProfile`` model form: used by users to edit their own
    profiles.
    """
    class Meta:
        model = UserProfile
        exclude = ('user', 'person')
