from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices

from django.contrib.auth.models import User

class UserProfile(models.Model):
    ALL = 1
    SOME = 2
    NONE = 3
    PRIVACY_LEVELS = Choices(
      (ALL, _('Open')),    
      (SOME, _('50/50')),
      (NONE, _('Tight')),
    )

    # This field is required.
    user = models.OneToOneField(User)

    # Other fields here
    is_public = models.BooleanField(_('is public'), default=True)
    privacy_level = models.IntegerField(_('privacy level'), choices=PRIVACY_LEVELS)
    wants_newsletter = models.BooleanField()
    
    def get_absolute_url(self):
        return ('profiles_profile_detail', (), { 'username': self.user.username })
    get_absolute_url = models.permalink(get_absolute_url)
    