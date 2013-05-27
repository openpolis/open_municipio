# -*- coding: utf-8 -*-
import datetime
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from optparse import make_option
from django.db.models.query_utils import Q
from open_municipio.people.models import municipality as m

import logging

from open_municipio.people.models import Person, Group, InstitutionCharge, Institution, GroupCharge, InstitutionResponsability, GroupResponsability


class Command(BaseCommand):
    """
    Check all members of the committees and look up for their original_charge_id.
    Original charge is the counselor charge related to the committee charge
    and it is used internally, in order to shorten the DOM navigation needed to
    retrieve a committee member's group or other responsabilities.

    The task add missing id, by default.
    It can also be launched so that it overwrites them all.
    """
    help = "Fix (or overwrite) all original_charge_id's"

    option_list = BaseCommand.option_list + (
        make_option('--dry-run',
                    action='store_true',
                    dest='dry_run',
                    default=False,
                    help='Only show changes, do not touch the DB'),
        make_option('--overwrite',
                    action='store_true',
                    dest='overwrite',
                    default=False,
                    help='Re-write charge from scratch'),
        )

    logger = logging.getLogger('webapp')

    def handle(self, **options):
        dry_run = options['dry_run']
        overwrite = options['overwrite']

        # fix logger level according to verbosity
        verbosity = options['verbosity']
        if verbosity == '0':
            self.logger.setLevel(logging.ERROR)
        elif verbosity == '1':
            self.logger.setLevel(logging.WARNING)
        elif verbosity == '2':
            self.logger.setLevel(logging.INFO)
        elif verbosity == '3':
            self.logger.setLevel(logging.DEBUG)

        self.logger.info("Inizio")

        council = m.council.as_institution

        # using municipality API (as m)
        for c in m.committees.as_institution():
            self.logger.info("Commissione: %s" % c)

            for ic in c.charge_set.all():
                try:
                    original_charge = council.charge_set.get(person=ic.person)
                except ObjectDoesNotExist:
                    self.logger.warning("  %s has no corresponding counselor. Skipping." % ic)
                    continue
                except MultipleObjectsReturned:
                    self.logger.warning("  %s has more than one corresponding counselor. Skipping." % ic)
                    continue

                if ic.original_charge != original_charge or overwrite:
                    self.logger.info("  %s will get the original charge: %s" % (ic, original_charge))
                    ic.original_charge = original_charge
                    if not dry_run:
                        ic.save()





