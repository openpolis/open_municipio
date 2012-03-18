from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices

from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    This is the user's profile.
    All infos about the user are here, except for those already in auth.User,
    that is: (username, first_name, last_name, email, password, 
              is_staff, is_active, is_superuser, last_login, date_joined)
    
    settings must contain: ``AUTH_PROFILE_MODULE = 'users.UserProfile'``
    
    From user to profile: ``user.get_profile()``
    From profile to user: ``profile.user``
    
    """
    PRIVACY_LEVELS = Choices(
        (1, 'all', _('all')),
        (2, 'some', _('some')),
        (3, 'none', _('none'))
    )

    # This field is required.
    user = models.OneToOneField(User)
    
    # user wants to be identified through his nickname,
    # his name will neve be shown publicly in the web site
    uses_nickname = models.BooleanField(_('show my nickname, not my name'), default=False)
    
    # the user has declared to be a politician
    # in the registration phase
    # this needs to be verified, before assigning the user to the Politicians group
    says_is_politician = models.BooleanField(_('i am a politician'), default=False)
    
    # user's privacy options
    privacy_level = models.IntegerField(_('privacy level'), choices=PRIVACY_LEVELS, default=PRIVACY_LEVELS.none)
    
    # user wants to receive newsletters (whatever that means)
    wants_newsletter = models.BooleanField(_('wants newsletter'), default=False)
    
    # TODO: location must be a foreign key to a proper, dedicated table
    city = models.CharField(_(u'location'), max_length=128)

    class Meta:
        db_table = u'users_user_profile'

    @models.permalink
    def get_absolute_url(self):
        return 'profiles_profile_detail', (), { 'username': self.user.username }
    
    @property
    def monitored_objects(self):
        """returns monitored objects as list of objects"""
        return [o.content_object for o in self.user.monitorings.all()]
    