import logging
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError

from django.contrib.auth.models import User
from open_municipio.users.models import UserProfile


class Command(BaseCommand):
    """
    This command should be a temporary patch for some problems in user registration that has not 
    been identified. For some reason, the django_social_auth PIPELINE allows to create a User
    instance without creating the UserProfile associated with it.

    This command identifies such User instances, create a UserProfile and outputs a warning
    message, so that we can (separately) communicate to them that they have to complete their
    profiles.
    """

    help = "Create a default UserProfile for those user that do not have one"

    option_list = BaseCommand.option_list + (
        make_option('--dryrun',
                    action='store_true',
                    dest='dryrun',      
                    default=False,
                    help='Do not create UserProfile'),
    )

    logger = logging.getLogger('webapp')

    def handle(self, **options):

        dryrun = options["dryrun"]
        users = User.objects.filter(userprofile=None)
 
        for u in users:
            self.logger.warning("User '%s' without user profile found." % u.username)
    
            if not dryrun:
                up = UserProfile.objects.create(user=u)
