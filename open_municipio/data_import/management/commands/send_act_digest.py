# -*- coding: utf-8 -*-
from optparse import make_option
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.core.management import BaseCommand
from open_municipio.acts.models import Act
from datetime import datetime, timedelta
from django.core.mail import EmailMultiAlternatives


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('-e', '--email', action='store', dest='email', default='',
                    help='Digest receiver/s email list (comma separated values without spaces)'),
    )

    help = 'Send a digest with latest imported act to some receivers'

    def handle(self, *args, **options):

        try:
            days = int(args[0])
        except (IndexError, ValueError):
            days = 1

        site_domain = Site.objects.get_current().domain

        yesterday = datetime.now() - timedelta(days=days)

        latest_act = Act.objects.filter(created__gt=yesterday)

        if not latest_act:
            return

        # initialize email dynamic fields
        receivers = options.get('email', '').strip()
        if receivers:
            receivers = receivers.split(',')
        else:
            receivers = User.objects.filter(groups__name=settings.DIGEST_DEFAULT_GROUP).values_list('email', flat=True)

        if not receivers:
            self.stdout.write('No receivers found\n')
            return

        self.stdout.write('Send a digest with latest {0} Act imported to {1} receivers\n'.format(
            len(latest_act), len(receivers)
        ))

        from_email = settings.DEFAULT_FROM_EMAIL
        subject = "OpenMunicipio - {0} : Lista degli atti importati".format(
            settings.SITE_INFO['main_city']
        )

        # compose text and html message
        message_html = "<ul>"
        text_content = ""
        for act in latest_act:
            url = "{0}/{1}".format(site_domain.rstrip('/'), act.get_absolute_url().lstrip('/'))
            message_html += '\n<li><a href="{0}">{1}</a>'.format(url, act)
            text_content += '\n{0}: {1}'.format(act.get_absolute_url(), act)
        message_html += '\n</ul>'

        # prepare email
        msg = EmailMultiAlternatives(subject, text_content, from_email, receivers)
        msg.attach_alternative(message_html, "text/html")

        msg.send()

        self.stdout.write('Email sent\n')




