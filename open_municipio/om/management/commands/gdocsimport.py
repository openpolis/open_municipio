# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from optparse import make_option

import gdata.docs
import gdata.docs.service
import gdata.spreadsheet.service

from open_municipio.people.models import Person, Group, InstitutionCharge, Institution, GroupCharge, InstitutionResponsability


class Command(BaseCommand):
    """
    Poiticians anagraphical data and their current and past charges are imported
    from a google spreadsheet.

    The title of the spreadsheet and access credentials are stored in local settings.

    Data may be compared or re-written. By default they're compared,
    to overwrite use the --overwrite option.
    """
    help = "Import historical charges from a google doc"

    option_list = BaseCommand.option_list + (
        make_option('--overwrite',
                    action='store_true',
                    dest='overwrite',
                    default=False,
                    help='Re-write charge from scratch'),
        )

    def handle(self, **options):
        # cleanup
        # Person.objects.all().delete()
        # InstitutionCharge.objects.all().delete()
        # Group.objects.all().delete()

        # get authorization parameters from settings
        username        = settings.GDOCS_IMPORT_USERNAME
        passwd          = settings.GDOCS_IMPORT_PASSWORD
        doc_name        = 'Storico degli incarichi Comune di Udine'

        # Connect to Google
        gd_client = gdata.spreadsheet.service.SpreadsheetsService()
        gd_client.email = username
        gd_client.password = passwd
        gd_client.source = 'openmunicipio.openpolis.it'
        gd_client.ProgrammaticLogin()

        # point to the right document
        q = gdata.spreadsheet.service.DocumentQuery()
        q['title'] = doc_name
        q['title-exact'] = 'true'
        feed = gd_client.GetSpreadsheetsFeed(query=q)

        # identify the spreadsheet feed
        spreadsheet_id = feed.entry[0].id.text.rsplit('/',1)[1]
        feed = gd_client.GetWorksheetsFeed(spreadsheet_id)

        # identify the worksheet feed
        worksheet_id = feed.entry[0].id.text.rsplit('/',1)[1]

        # fetch the rows
        rows = gd_client.GetListFeed(spreadsheet_id, worksheet_id).entry

        # iterate through the rows
        name = None
        for row in rows:
            # get or remember name
            if row.custom['nome'].text:
                name = row.custom['nome'].text
                sex = row.custom['sesso'].text
                birth_date = row.custom['datanascita'].text
                birth_location = row.custom['luogonascita'].text
                self.stdout.write("%s (%s) - nascita: %s a %s" % (name, sex, birth_date, birth_location))

            # get dates
            date_start = row.custom['dal'].text
            date_end = row.custom['al'].text

            cg = row.custom['incaricoogruppo'].text
            if cg.lower()[0:6] == 'gruppo':
                if ':' in cg[7:]:
                    group, charge = cg[7:].split(':')
                    charge = charge.strip()
                else:
                    group = cg[7:]
                    charge = 'Membro'

                self.stdout.write("    %s - gruppo: %s - dal %s al %s" % (charge, group, date_start, date_end))
            else:
                self.stdout.write("    %s - dal %s al %s" % (cg, date_start, date_end))
