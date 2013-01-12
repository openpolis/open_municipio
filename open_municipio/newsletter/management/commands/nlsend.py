import logging
from optparse import make_option
from datetime import datetime
from django.core.management.base import LabelCommand, BaseCommand, CommandError
from django.db.models.query import EmptyQuerySet

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

from open_municipio.monitoring.models import Monitoring
from open_municipio.newscache.models import News
from open_municipio.newsletter.models import Newsletter
from open_municipio.users.models import UserProfile

class Command(LabelCommand):
    """
    Fetch and send emails containing news on monitored objects.

    The --dryrun option allows to preview which mails will be sent, without actually send them

    """
    help = "Fetch and send emails to subscribed users"

    option_list = BaseCommand.option_list + (
        make_option('--dryrun',
                    action='store_true',
                    dest='dryrun',
                    default=False,
                    help='Do not send emails'),
        make_option('--preview',
                    action='store_true',
                    dest='preview',
                    default=False,
                    help='Preview emails and news, without sending them'),
        make_option('--from-date',
                    dest='fromdate',
                    help='Fetches news from this date, overrides ordinary last newsletter date filtering'),
    )

    args = '<user_email>'
    label = 'user email'
    logger = logging.getLogger('import')

    plaintext_tpl = get_template('email.txt')
    htmly_tpl     = get_template('email.html')


    def handle(self, *labels, **options):


        # fix logger level according to verbosity
        verbosity = options['verbosity']
        if verbosity == '0':
            self.logger.setLevel(logging.ERROR)
        elif verbosity == '1':
            self.logger.setLevel(logging.INFO)
        elif verbosity >= '2':
            self.logger.setLevel(logging.DEBUG)


        # preview is a predefined settings
        if options['preview']:
            options['dryrun'] = True
            self.logger.setLevel(logging.DEBUG)

        n_sent_mails = 0

        nl = Newsletter()
        if not options['dryrun']:
            nl.save()

        if not labels:
            nlprofiles = UserProfile.objects.filter(wants_newsletter=True)
        else:
            nlprofiles = UserProfile.objects.filter(wants_newsletter=True, user__email__in=labels)


        # fetch last sent newsletter's timestamp
        nls = Newsletter.objects.filter(finished__isnull=False).order_by('-finished')
        if nls:
            from_date = nls[0].started
            # highjack fromdate options, if not already defined
            if not options['fromdate']:
                options['fromdate'] = from_date

        if options['fromdate']:
            self.logger.info('fetching news from: {0}'.format(options['fromdate']))

        for profile in nlprofiles:
            n_sent_mails += self.handle_label(profile, **options)

        nl.n_mails = n_sent_mails
        nl.finished = datetime.now()
        if not options['dryrun']:
            nl.save()

    def handle_label(self, profile, **options):
        """
        fetch newsletter and send email to a single user
        return the number of mail sent
        """
        self.logger.info('-------------')
        self.logger.info(u'user: {0}'.format(profile.user))
        mos = profile.monitored_objects
        if not mos:
            self.logger.debug(u' not monitoring')
            return 0
        else:
            self.logger.debug(u' monitoring these objects:')
            # extract the news related to all objects that the user is monitoring
            # filter: institutional news of highest priority, only
            user_news = EmptyQuerySet()
            for mo in mos:
                related_news = mo.related_news.\
                    filter(news_type=News.NEWS_TYPE.institutional).\
                    filter(priority=1)

                # add date filter if required
                if options['fromdate']:
                    related_news = related_news.filter(created__gt=options['fromdate'])

                # add objects related news to user news
                user_news |= related_news

                # log at debug level, for previewing
                self.logger.debug(u' -{0}, with {1} news'.format(mo.__unicode__()[:60], related_news.count()))
                for news in related_news:
                    self.logger.debug(u'   *{0}'.format(news))

            n_news = len(user_news)
            if n_news:
                if not options['dryrun']:
                    d = Context({ 'profile': profile,
                                  'user_news': [{'date': rn.news_date, 'text': rn.text} for rn in user_news]})

                    subject, from_email, to = 'hello', 'noreply@openmunicipio.it', 'guglielmo@celata.com'
                    text_content = self.plaintext_tpl.render(d)
                    html_content = self.htmly_tpl.render(d)
                    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                    self.logger.info(u'mail with {0} news sent'.format(n_news))
                else:
                    self.logger.info(u'mail with {0} news would be sent (dryrun)'.format(n_news))

            else:
                self.logger.info(u'no news to send')
            return n_news > 0
