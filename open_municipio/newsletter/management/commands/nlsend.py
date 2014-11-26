import logging
from optparse import make_option
from datetime import datetime
from django.contrib.sites.models import Site
from django.core.management.base import LabelCommand, BaseCommand, CommandError
from django.db.models.query import EmptyQuerySet
from django.db import models
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.conf import settings
from django.utils import translation

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
    logger = logging.getLogger('webapp')

    plaintext_tpl = get_template('email.txt')
    htmly_tpl     = get_template('email.html')


    def handle(self, *labels, **options):

        translation.activate(settings.LANGUAGE_CODE)

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
            nlprofiles = UserProfile.objects.filter(wants_newsletter=True, user__email__isnull=False).exclude(user__email='')
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

        translation.deactivate()


    def handle_label(self, profile, **options):
        """
        fetch newsletter and send email to a single user
        return the number of mail sent
        """
        self.logger.info('-------------')
        self.logger.info(u'user: {0} - {1}'.format(profile.user, profile.user.email))
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

                # in case of deleted objects being monitored yet (needs fix?)
                if mo == None: continue

                related_news = mo.related_news.\
                    filter(
                        models.Q(news_type=News.NEWS_TYPE.institutional, 
                            priority__lte=2) 
                    | 
                        models.Q(news_type=News.NEWS_TYPE.community, 
                            priority=1)
                    )

                # add date filter if required
                if options['fromdate']:
                    related_news = related_news.filter(modified__gt=options['fromdate'])

                # add objects related news to user news
                user_news |= related_news

                # log at debug level, for previewing
                self.logger.debug(u' -{0}, with {1} news'.format(mo.__unicode__()[:60], related_news.count()))
                for news in related_news:
                    self.logger.debug(u'   * ({0}) {1}'.format(news.created, news))

            import re
            site_domain = Site.objects.get(pk=settings.SITE_ID)

            n_news = len(user_news)
            if n_news:
                if not options['dryrun']:

                    ordered_user_news = [{'date': rn.news_date, 'text': re.sub('href=\"\/', 'href="http://{0}/'.format(site_domain), rn.text)} for rn in user_news]

                    # NB this can work only if k["date"] is always not None
                    ordered_user_news = sorted(ordered_user_news, key=lambda k: k["date"], reverse=True)

                    d = Context({ 'site_home': settings.SITE_INFO['home'],
                                  'profile': profile,
                                  'city': settings.SITE_INFO['main_city'],
                                  'webmaster': settings.WEBMASTER_INFO,
                                  'user_news': ordered_user_news,
                                })

                    subject, from_email, to = settings.NL_TITLE, settings.NL_FROM, profile.user.email
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
