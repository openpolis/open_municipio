# -*- coding: utf-8 -*-
import datetime
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from optparse import make_option
from django.db.models.query_utils import Q

import gdata.docs
import gdata.docs.service
import gdata.spreadsheet.service

from open_municipio.people.models import Person, Group, InstitutionCharge, Institution, GroupCharge, InstitutionResponsability, GroupResponsability


class Command(BaseCommand):
    """
    Poiticians anagraphical data and their current and past charges are imported
    from a google spreadsheet.

    Access credentials are stored in local settings.

    Data may be compared or re-written. By default they're compared,
    to overwrite use the --overwrite option.
    """
    help = "Import historical charges from a google doc"

    option_list = BaseCommand.option_list + (
        make_option('--title',
                    dest='title',
                    help='Title of the google document (use quotes)'),
        make_option('--overwrite',
                    action='store_true',
                    dest='overwrite',
                    default=False,
                    help='Re-write charge from scratch'),
        )

    def handle(self, **options):
        """
        access the google spreadsheet,
        fetch institutional and group charges and responsabilities;

        * skip overlapping analogues in the model,
        * use exact copies if found,
        * create new charge if nothing found
        """

        # title is necessary
        if options['title'] is None:
            raise Exception("title must be specified with the --title option")

        doc_name        = options['title']

        # connectoin to Google
        gd_client = gdata.spreadsheet.service.SpreadsheetsService()
        gd_client.email = settings.GOOGLE_USERNAME
        gd_client.password = settings.GOOGLE_PASSWORD
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
                first_name = row.custom['nome'].text.encode('utf-8')
                last_name = row.custom['cognome'].text.encode('utf-8')
                sex = row.custom['sesso'].text
                if sex == 'M':
                    sex = Person.MALE_SEX
                else:
                    sex = Person.FEMALE_SEX

                birth_date = datetime.datetime.strptime(row.custom['datanascita'].text, '%d/%m/%Y').strftime('%Y-%m-%d')
                birth_location = row.custom['luogonascita'].text
                self.stdout.write("%s %s (%s) - nascita: %s a %s\n" %
                                  (first_name, last_name, sex,
                                   birth_date,
                                   birth_location))


                # fetch or create person
                p, p_created = Person.objects.get_or_create(
                    first_name=first_name,
                    last_name=last_name,
                    birth_date=birth_date,
                    sex=sex
                )
                if p_created or options['overwrite']:
                    p.birth_location = birth_location
                    p.save()


            # get charge start and end dates
            date_start = datetime.datetime.strptime(row.custom['dal'].text, '%d/%m/%Y').strftime('%Y-%m-%d')
            if row.custom['al'].text:
                date_end = datetime.datetime.strptime(row.custom['al'].text, '%d/%m/%Y').strftime('%Y-%m-%d')
            else:
                date_end = None

            cg = row.custom['incaricoogruppo'].text.encode('utf-8')
            if cg.lower()[0:6] == 'gruppo':
                if ':' in cg[7:]:
                    group, charge_description = cg[7:].split(':')
                    responsability = charge_description.strip()
                else:
                    group = cg[7:]
                    responsability = 'Membro'


                self.stdout.write("    %s - gruppo: %s - dal %s al %s\n" %
                                  (responsability, group,
                                   date_start,
                                   date_end
                                  )
                )

                # get or create group
                g, g_created = Group.objects.get_or_create(
                    name=group.strip(),
                )

                # get counselor charge linked to group charge
                try:
                    if date_end is None:
                        charge = p.all_institution_charges.get(
                            Q(institution__institution_type=Institution.COUNCIL),
                            Q(end_date__gte=date_start) | Q(end_date__isnull=True)
                        )
                    else:
                        charge = p.all_institution_charges.get(
                            Q(institution__institution_type=Institution.COUNCIL),
                            Q(start_date__lte=date_end),
                            Q(end_date__gte=date_start) | Q(end_date__isnull=True)
                        )
                except ObjectDoesNotExist:
                    self.stderr.write("Error: group charge cannot be linked to counselor (none found). Skipping\n")
                    continue
                except MultipleObjectsReturned:
                    self.stderr.write("Error: group charge cannot be linked to counselor (multiple found). Skipping\n")
                    continue

                # group charge
                # check is complex (overlapping dates involved)

                # check overlapping charges
                if date_end is None:
                    n_overlapping_gcs = GroupCharge.objects.filter(
                        Q(group=g), Q(charge=charge),
                        Q(end_date__gte=date_start) | Q(end_date__isnull=True)
                    ).count()
                else:
                    n_overlapping_gcs = GroupCharge.objects.filter(
                        Q(group=g), Q(charge=charge),
                        Q(start_date__lte=date_end),
                        Q(end_date__gte=date_start) | Q(end_date__isnull=True)
                    ).count()
                if not n_overlapping_gcs:
                    #create new charge
                    gc = GroupCharge.objects.create(
                        group=g, charge=charge,
                        start_date=date_start,
                        end_date=date_end
                    )
                    self.stdout.write("      Creating new group charge (%s - %s)\n" % (date_start, date_end))
                else:
                    # check if exact charge is there
                    try:
                        gc = GroupCharge.objects.get(
                            group=g, charge=charge,
                            start_date=date_start,
                            end_date=date_end
                        )
                        self.stdout.write("      Using existing group charge (%s - %s)\n" % (date_start, date_end))
                    except ObjectDoesNotExist:
                        self.stderr.write("Warning: group charge overlapped by existing charges. Skipping charge.\n")

                # group responsability
                if responsability != 'Membro':
                    if responsability.lower() == 'presidente':
                        r_type = GroupResponsability.CHARGE_TYPES.leader
                    elif responsability.lower() == 'vice presidente':
                        r_type = GroupResponsability.CHARGE_TYPES.deputy
                    else:
                        r_type = None

                    if r_type is not None:
                        # check overlapping responsabilities
                        if date_end is None:
                            n_overlapping_grs = GroupResponsability.objects.filter(
                                Q(charge_type=r_type),
                                Q(charge=gc),
                                Q(end_date__gte=date_start) | Q(end_date__isnull=True)
                            ).count()
                        else:
                            n_overlapping_grs = GroupResponsability.objects.filter(
                                Q(charge_type=r_type),
                                Q(charge=gc),
                                Q(start_date__lte=date_end),
                                Q(end_date__gte=date_start) | Q(end_date__isnull=True)
                            ).count()
                        if not n_overlapping_grs:
                            # create new responsability
                            r = GroupResponsability.objects.create(
                                charge_type=r_type,
                                charge=gc,
                                start_date=date_start,
                                end_date=date_end
                            )
                            self.stdout.write("      Creating new group resp (%s - %s)\n" % (date_start, date_end))
                        else:
                            # check if exact responsability is there
                            try:
                                r = GroupResponsability.objects.get(
                                    charge_type=r_type, charge=charge,
                                    start_date=date_start,
                                    end_date=date_end
                                )
                                self.stdout.write("      Using existing group resp (%s - %s)\n" % (date_start, date_end))
                            except ObjectDoesNotExist:
                                self.stderr.write("Error: group resp overlapped by existing charges. Skipping\n")
                                continue

            else:
                # assign institution
                if cg == 'Assessore':
                    charge_institution = Institution.objects.get(institution_type=Institution.CITY_GOVERNMENT)
                elif cg == 'Consigliere' or 'consiglio comunale' in cg.lower():
                    charge_institution = Institution.objects.get(institution_type=Institution.COUNCIL)
                else:
                    self.stderr.write("Warning: charge must be Consigliere or Assessore. Skipping charge %s\n" % cg)

                self.stdout.write("    %s - dal %s al %s\n" %
                                  (cg,
                                   date_start,
                                   date_end))

                # check or add charge only for counselors or assessors
                if not 'presidente' in cg.lower() and not 'vice' in cg.lower():
                    # check overlapping charges
                    if date_end is None:
                        n_overlapping_cs = InstitutionCharge.objects.filter(
                            Q(person=p),
                            Q(institution=charge_institution),
                            Q(end_date__gte=date_start) | Q(end_date__isnull=True)
                        ).count()
                    else:
                        n_overlapping_cs = InstitutionCharge.objects.filter(
                            Q(person=p),
                            Q(institution=charge_institution),
                            Q(start_date__lte=date_end),
                            Q(end_date__gte=date_start) | Q(end_date__isnull=True)
                        ).count()
                    if not n_overlapping_cs:
                        # create new charge
                        ic = InstitutionCharge.objects.create(
                            person=p,
                            institution=charge_institution,
                            start_date=date_start,
                            end_date=date_end
                        )
                        self.stdout.write("      Creating new charge (%s - %s)\n" % (date_start, date_end))
                    else:
                        # check if exact charge is there
                        try:
                            ic = InstitutionCharge.objects.get(
                                Q(person=p),
                                Q(institution=charge_institution),
                                Q(start_date=date_start),
                                Q(end_date=date_end)
                            )
                            self.stdout.write("      Using existing charge (%s - %s)\n" % (date_start, date_end))
                        except ObjectDoesNotExist:
                            self.stderr.write("Error: charge overlapped by existing charges. Skipping\n")
                            continue

                # institution charge responsability
                if cg.lower()[0:10] == 'presidente':
                    r_type = InstitutionResponsability.CHARGE_TYPES.president
                elif cg.lower()[0:4] == 'vice':
                    r_type = InstitutionResponsability.CHARGE_TYPES.vice
                else:
                    r_type = None

                if r_type is not None:
                    # check overlapping responsabilities
                    if date_end is None:
                        n_overlapping_grs = InstitutionResponsability.objects.filter(
                            Q(charge_type=r_type),
                            Q(charge=ic),
                            Q(end_date__gte=date_start) | Q(end_date__isnull=True)
                        ).count()
                    else:
                        n_overlapping_grs = InstitutionResponsability.objects.filter(
                            Q(charge_type=r_type),
                            Q(charge=ic),
                            Q(start_date__lte=date_end),
                            Q(end_date__gte=date_start) | Q(end_date__isnull=True)
                        ).count()
                    if not n_overlapping_grs:
                        # create new responsability
                        ir = InstitutionResponsability.objects.create(
                            charge_type=r_type,
                            charge=ic,
                            start_date=date_start,
                            end_date=date_end
                        )
                        self.stdout.write("      Creating new institution resp (%s - %s)\n" % (date_start, date_end))

