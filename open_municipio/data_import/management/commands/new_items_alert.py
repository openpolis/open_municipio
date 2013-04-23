# -*- coding: utf-8 -*-
import logging
from optparse import make_option
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.core.management import BaseCommand
from open_municipio.acts.models import Act
from datetime import datetime, timedelta
from django.core.mail import EmailMultiAlternatives, mail_managers
from open_municipio.people.models import Sitting
from open_municipio.votations.models import Votation


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('-e', '--email', action='store', dest='email', default='',
                    help='Digest receiver/s email list (comma separated values without spaces)'),
    )

    help = 'Send a digest with latest imported acts to some receivers'
    logger = logging.getLogger('import')

    def handle(self, *args, **options):

        try:
            days = int(args[0])
        except (IndexError, ValueError):
            days = 1

        # fix logger level according to verbosity
        verbosity = options['verbosity']
        if verbosity == '0':
            self.logger.setLevel(logging.ERROR)
        elif verbosity == '1':
            self.logger.setLevel(logging.INFO)
        elif verbosity >= '2':
            self.logger.setLevel(logging.DEBUG)

        site_domain = Site.objects.get_current().domain

        time_period = datetime.now() - timedelta(days=days)
        acts = Act.objects.filter(created__gt=time_period)
        sittings = Sitting.objects.filter(created__gt=time_period)

        self.logger.info('Period: {0}'.format(time_period))

        if not acts and not sittings:
            self.logger.info('no new acts or sittings have been imported')
            return

        # initialize email dynamic fields
        receivers = options.get('email', '').strip()
        if receivers:
            receivers = receivers.split(',')
        else:
            receivers = User.objects.filter(groups__name=settings.DIGEST_DEFAULT_GROUP).values_list('email', flat=True)

        if not receivers:
            self.logger.error('No receivers found!')
            return


        self.logger.info('Sending a digest with latest {0} Acts and {1} Sittings imported to {2} receivers\n'.format(
            len(acts), len(sittings), len(receivers)
        ))

        from_email = settings.SERVER_EMAIL
        subject = "[OpenMunicipio - {0}] : Lista nuovi atti e sedute".format(
            settings.SITE_INFO['main_city']
        )

        # compose text and html message
        message_html = "<h3>Atti</h3>"
        text_content = "Atti\n----\n"
        self.logger.info("{0} new acts have been created".format(len(acts)))
        message_html += "<ul>"
        for act in acts:
            url = "http://{0}/{1}".format(site_domain.rstrip('/'), act.get_absolute_url().lstrip('/'))
            message_html += '\n<li><a href="{0}">{1}</a>'.format(url, act)
            text_content += '\n{0}: {1}'.format(act.get_absolute_url(), act)
            self.logger.debug('  {0}: {1}'.format(act.get_absolute_url(), act))
        message_html += '\n</ul>'

        self.logger.info("{0} new sittings have been created".format(len(sittings)))
        message_html += "<br/><h3>Votazioni</h3><br/><ul>"
        text_content += "Votazioni\n---------\n"
        for sitting in sittings:
            message_html += '\n<li><dl><dt>{0}</dt>'.format(sitting)
            text_content += '\n{0}'.format(sitting)
            self.logger.debug('  {0}'.format(sitting))
            for votation in sitting.votation_set.all():
                url = "http://{0}/{1}".format(site_domain.rstrip('/'), votation.get_absolute_url().lstrip('/'))
                message_html += '\n<dd><a href="{0}">{1}</a></dd>'.format(url, votation)
                text_content += '\n\t{0}: {1}'.format(url, votation)
                self.logger.debug('    {0}: {1}'.format(url, votation))
        message_html += '\n</dl></li></ul>'

        # send email to managers
        mail_managers(
            subject, text_content, html_message=message_html
        )
        msg = EmailMultiAlternatives(subject, text_content, from_email, receivers)
        msg.attach_alternative(message_html, "text/html")

        msg.send()

        self.logger.info('Emails sent')




