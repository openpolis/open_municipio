import logging
from optparse import make_option
from django.core.management import BaseCommand
from open_municipio.users.models import UserProfile

class Command(BaseCommand):
    """
    List users with their subscription date
    Use --newsletter to fetch only those wanting the newsletter
    """
    help = "List users, with their subscription date"

    option_list = BaseCommand.option_list + (
        make_option('--newsletter',
                    action='store_true',
                    dest='newsletter',
                    default=False,
                    help='Fetch only users wanting newsletter'),
        )

    logger = logging.getLogger('webapp')

    def handle(self, **options):
        """
        access users profiles an show details for each user wanting the newsletter
        """
        profiles = UserProfile.objects.all()
        if options['newsletter']:
            profiles = profiles.filter(wants_newsletter=True)

        print "Nome, Email, DataIscrizione, DataUltimoLogin"
        for profile in profiles:
            print u'{u}, {u.email}, {u.date_joined}, {u.last_login}'.format(u=profile.user)

