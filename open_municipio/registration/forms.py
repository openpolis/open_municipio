"""
Forms and validation code for user registration.

"""


from registration.forms import RegistrationForm
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


# I put this on all required fields, because it's easier to pick up
# on them with CSS or JavaScript if they have a class of "required"
# in the HTML. Your mileage may vary. If/when Django ticket #3515
# lands in trunk, this will no longer be necessary.
attrs_dict = {'class': 'required'}


class OMRegistrationForm(RegistrationForm):
    """
    Subclass of ``RegistrationForm`` which extends the default registration backend,
    adding some features needed in Open Municipio:
    
    * it adds two required checkboxes, for agreeing to a site's Terms of Service 
      and to the privacy conditions
    * it ensures email uniqueness
    * it doesn't accept email address from domains such as mailinator, for (weak) spam protection
    """
    tos = forms.BooleanField(widget=forms.CheckboxInput(attrs=attrs_dict),
                             label=_(u'I have read and agree to the Terms of Service'),
                             error_messages={'required': _("You must agree to the terms to register")})
    pri = forms.BooleanField(widget=forms.CheckboxInput(attrs=attrs_dict),
                             label=_(u'I have read and agree to the Privacy conditions'),
                             error_messages={'required': _("You must agree to the conditions to register")})
    
    
    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.
        
        """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(_("This email address is already in use. Please supply a different email address."))
        
        # TODO: check against a DEA blacklist (see block-disposable-email.com)
        
        return self.cleaned_data['email']


