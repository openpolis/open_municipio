import logging
from optparse import make_option
from django.core.management import BaseCommand
from django.db.models.query import EmptyQuerySet
from open_municipio.monitoring.models import Monitoring
from open_municipio.newscache.models import News
from open_municipio.users.models import UserProfile

class Command(BaseCommand):
    """
    List users that want newsletter messages, with some status details
    - name, email, last received message, next messages to be sent
    """
    help = "List users that want newsletter messages"

    option_list = BaseCommand.option_list

    logger = logging.getLogger('import')

    def handle(self, **options):
        """
        access users profiles an show details for each user wanting the newsletter
        """
        nlprofiles = UserProfile.objects.filter(wants_newsletter=True)
        for profile in nlprofiles:
            mos = Monitoring.objects.filter(user=profile.user)

            # extract the news related to all objects that the user is monitoring
            news = EmptyQuerySet()
            for mo in mos:
                news |= mo.content_object.related_news

            # filter: fetch institutional news of highest priority
            n_news = news.filter(news_type=News.NEWS_TYPE.institutional).filter(priority=1).count()

            print u'{u.first_name} {u.last_name} ({u.username}) - n_news: {0}'.format(n_news, u=profile.user)

