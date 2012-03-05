from django.conf import settings
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site

from registration import signals
from open_municipio.registration.forms import OMRegistrationForm
from registration.backends.default import DefaultBackend


class OMBackend(DefaultBackend):
    """
    
    """
    def get_form_class(self, request):
        """
        Return the default form class used for user registration.
        
        """
        return OMRegistrationForm

