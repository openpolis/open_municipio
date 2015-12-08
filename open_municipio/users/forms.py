#!/usr/bin/python
# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.forms.models import ModelForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from model_utils import Choices
from registration.forms import RegistrationForm, RegistrationFormUniqueEmail
from sorl.thumbnail.admin.current import AdminImageWidget
from open_municipio.locations.models import Location

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
    first_name = forms.CharField(max_length=30, label=_('First Name'))
    last_name = forms.CharField(max_length=30, label=_('Last Name'))
    uses_nickname = forms.BooleanField(widget=forms.CheckboxInput(attrs=attrs_dict),
                                       label=_(u'I want only my nickname to be publicly shown'),
                                       help_text=u"Indica se preferisci che nel sito venga mostrato esclusivamente il tuo nome utente",
                                       required=False)
    says_is_politician = forms.BooleanField(required=False, label=_('I am a politician'),
                                            help_text=u"Segnala alla redazione che sei un politico del municipio, per avere accesso avanzato.")
    wants_newsletter = forms.BooleanField(required=False, label=_('Wants newsletter'),)
    wants_newsletter_blog = forms.BooleanField(required=False, label=_('Wants blog newsletter'),)

    location = forms.ModelChoiceField(required=False, queryset=Location.objects.order_by("name"), label=_('Location, if applicable'),
                                      help_text=u"Se sei cittadino di %s, scegli la zona della città in cui risiedi" % settings.SITE_INFO['main_city'])
    description = forms.CharField(required=False, label=_('Description'), widget=forms.Textarea(),
                                  help_text=u"Una breve descrizione di te, che apparirà nel tuo profilo")
    image = forms.ImageField(required=False, label=_('Your image'),
                             help_text="L'immagine che scegli verrà ridimensionata nelle dimensioni di 100x100 pixel")
    tos = forms.BooleanField(widget=forms.CheckboxInput(attrs=attrs_dict),
                             label=_(u'I have read and approve the Terms of Service'),
                             error_messages={'required': _("You must agree to the terms to register")})
    pri = forms.BooleanField(widget=forms.CheckboxInput(attrs=attrs_dict),
                             label=_(u'I have read and agree to the Privacy conditions'),
                             error_messages={'required': _("You must agree to the conditions to register")})


    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        
        if not settings.UI_LOCATIONS:
            del self.fields["location"]

class SocialIntegrationForm(forms.Form):
    """
    ``User`` model form for social registration: collecting
    some extra data not provided by social networks.
    """
    uses_nickname = forms.BooleanField(widget=forms.CheckboxInput(attrs=attrs_dict),
                                       label=_(u'I want only my nickname to be publicly shown'),
                                       help_text=u"Indica se preferisci che nel sito venga mostrato esclusivamente il tuo nome utente",
                                       required=False)
    says_is_politician = forms.BooleanField(required=False, label=_('I am a politician'),
                                            help_text=u"Segnala alla redazione che sei un politico del municipio, per avere accesso avanzato.")
    wants_newsletter = forms.BooleanField(required=False, label=_('Wants newsletter'))
    wants_newsletter_blog = forms.BooleanField(required=False, label=_('Wants blog newsletter'))

    location = forms.ModelChoiceField(required=False, queryset=Location.objects.order_by("name"), label=_('Location, if applicable'),
                                      help_text=u"Se sei cittadino di %s, scegli la zona della città in cui risiedi" % settings.SITE_INFO['main_city'])
    tos = forms.BooleanField(widget=forms.CheckboxInput(attrs=attrs_dict),
                             label=_(u'I have read and approve the Terms of Service'),
                             error_messages={'required': _("You must agree to the terms to register")})
    pri = forms.BooleanField(widget=forms.CheckboxInput(attrs=attrs_dict),
                             label=_(u'I have read and agree to the Privacy conditions'),
                             error_messages={'required': _("You must agree to the conditions to register")})

    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.
        """
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(_("A user with that username already exists."))



class SocialTwitterIntegrationForm(SocialIntegrationForm):
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,maxlength=75)),
                             label=_("E-mail"),
                             help_text="Twitter non fornisce l'email della tua utenza, che ci è necessaria per comunicare con te. La tua email non verrà divulgata o pubblicata sul sito.")


class ProfileSocialRegistrationForm(ModelForm):
    """
    ``UserProfile`` model form for social registration: collecting
    some extra data not provided by social networks.
    """
    class Meta:
        model = UserProfile
        exclude = ('user', 'person', 'privacy_level')


class UserProfileForm(ModelForm):
    """
    ``UserProfile`` model form: used by users to edit their own
    profiles.
    """
    image = forms.ImageField(required=False, label=u"La tua immagine", widget=AdminImageWidget)

    class Meta:
        model = UserProfile
        exclude = ('user', 'person', 'privacy_level')
