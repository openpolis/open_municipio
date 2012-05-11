# -*- coding: utf-8 -*-
from optparse import make_option
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.management.base import LabelCommand, CommandError, BaseCommand

from lxml import etree
from os import path

from open_municipio.people.models import Sitting, Institution, Person
from open_municipio.votations.models import Votation, ChargeVote, InstitutionCharge

import dateutil.parser
#from time import strptime
#import datetime
import traceback
from open_municipio import settings_import as settings


# configure xml namespaces
NS = {
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'om': 'http://www.openmunicipio.it',
    'xlink': 'http://www.w3.org/1999/xlink'
}

class Command(LabelCommand):
    option_list = BaseCommand.option_list + (
        make_option('--overwrite',
                    action='store_true',
                    dest='overwrite',
                    default=False,
                    help='Re-write charge from scratch'
        ),
        make_option('--people_file',
                    dest='people_file',
                    default='import_tmp/udine/votations/people.xml',
                    help='The xml file containing the persons'
        ),
    )

    args = "<filename filename ...>"
    help = "Import the voting information contained in the specified XML documents"
    label = 'filename'

    people_tree = None

    def lookupCharge(self, xml_chargevote, institution, **options):
        """
        look for the correct open municipio charge, or return None
        """
        try:
            # this is done through component_id,
            # making the whole ChargeXRef stuff unused
            # TODO: see if there's a more flexible way to do it, using ChargeXRef
            component_id = xml_chargevote.get("componentId")
            people_charges = self.people_tree.xpath(
                '//om:Person[@id=%s]' % component_id,
                namespaces={'om': "http://www.openmunicipio.it"}
            )
            if len(people_charges):
                om_id = people_charges[0].get('om_id')
                if om_id is None:
                    if int(options['verbosity']) > 0:
                        self.stderr.write("Warning: charge with id %s has no om_id (past charge?). Skipping.\n" % component_id)
                    return None
                try:
                    person = Person.objects.get(pk=int(om_id))
                    charge =  person.current_institution_charge(institution)
                    return charge
                except ObjectDoesNotExist:
                    if int(options['verbosity']) > 1:
                        self.stderr.write("Warning: could not find person or charge for id = %s in open municipio DB. Skipping.\n" % component_id)
                    return None
                except MultipleObjectsReturned:
                    self.stderr.write("Error: found more than one person or charge for id %s in open municipio db. Skipping.\n" % component_id)
                    return None
            else:
                if int(options['verbosity']) > 0:
                    self.stderr.write("Warning: could not find person for id %s in peopkle XML file. Skipping.\n" % component_id)
                return None
        except ObjectDoesNotExist:
            if int(options['verbosity']) > 0:
                self.stderr.write("Warning: could not find charge with id %s in Open Municipio DB. Skipping.\n" % component_id)
            return None


    def handle_label(self, filename, **options):
        if not path.isfile(filename):
            raise IOError("File %s does not exist" % filename)

        tree = etree.parse(filename)

        sittings = tree.xpath("/om:Sitting",namespaces=NS)
        self.stdout.write("%d Sittings to import\n" % len(sittings))
        for xml_sitting in sittings:

            # map the sitting site code into an Institution
            site = xml_sitting.get("site")
            if site is None:
                self.stderr.write(
                    "Error: Sitting %s has no site attribute! Skipping this sitting." %
                    xml_sitting.get('num')
                )
                continue


            # get or create the sitting object
            curr_inst = Institution.objects.get(name=settings.XML_TO_OM_INST[site])
            council_inst = Institution.objects.get(name=settings.XML_TO_OM_INST['SCN'])

            sitting_date = xml_sitting.get("date")[0:10]
            om_sitting, created = Sitting.objects.get_or_create(
                number=xml_sitting.get("num"),
                date=sitting_date,
                institution=curr_inst
            )

            if not created:
                self.stdout.write("\n\nFound sitting %s - %s\n" % (om_sitting.number, sitting_date))
            else:
                self.stdout.write("\n\nCreated sitting %s - %s\n" % (om_sitting.number, sitting_date))

            # fetch all votations for the sitting in the XML
            votations = xml_sitting.xpath("./om:Votation", namespaces=NS)
            self.stdout.write("%d Votations to import\n" % len(votations))
            for xml_votation in votations:

                vot_num = xml_votation.get("seq_n")
                if vot_num is None:
                    self.stderr.write(
                        "Votation has no seq_n attribute! Skipping it."
                    )
                    continue

                # get or create the sitting in the DB
                om_votation, created = Votation.objects.get_or_create(
                    idnum=vot_num,
                    sitting=om_sitting
                )
                if not created:
                    self.stdout.write("Found votation %s\n" % om_votation.idnum)
                else:
                    self.stdout.write("Created votation %s\n" % om_votation.idnum)

                # new votations get statistics (or overwrite)
                if created or options['overwrite']:
                    subjects = xml_votation.xpath("./om:Subject", namespaces=NS)
                    if len(subjects):
                        om_votation.act_descr = subjects[0].text or subjects[0].get('sintetic') or ""

                    # these data MUST be cross-verified with detailed data
                    # om_votation.n_presents = xml_votation.get("presents")
                    # om_votation.n_legal = xml_votation.get("legal_number")
                    # om_votation.n_yes = xml_votation.get("counter_yes")
                    # om_votation.n_no = xml_votation.get("counter_no")
                    # om_votation.n_abst = xml_votation.get("counter_abs")
                    # om_votation.outcome = xml_votation.get("outcome") # decode
                    om_votation.save()

                self.stdout.write("title: %s\n" % om_votation.act_descr.encode('utf-8'))

                # build a ChargeVote for every single vote
                chargevotes = xml_votation.xpath("./om:Votes/om:ChargeVote", namespaces=NS)
                self.stdout.write("Votation contains %d ChargeVotes\n" % len(chargevotes))

                # remove all votes in this votation if overwriting
                if options['overwrite']:
                    ChargeVote.objects.filter(votation=om_votation).delete()

                for xml_cv in chargevotes:
                    # lookup council charges to match with ChargeVote
                    om_charge = self.lookupCharge(xml_cv, council_inst, **options)
                    if om_charge is None:
                        continue

                    # get or create ChargeVote
                    om_cv, created = ChargeVote.objects.get_or_create(
                        charge=om_charge,
                        votation=om_votation
                    )

                    if created or options['overwrite']:
                        xml_vote = xml_cv.get("vote")
                        if not (xml_vote in settings.XML_TO_OM_VOTE):
                            self.stderr.write(
                                "Cannot store ChargeVote. XML vote code '%d' not recognized. Skipping." %
                                xml_vote
                            )
                            continue
                        if settings.XML_TO_OM_VOTE[xml_vote] is None:
                            self.stderr.write(
                                "Skipping non installed terminals, as not interesting. "
                            )
                            continue

                        om_cv.vote = settings.XML_TO_OM_VOTE[xml_vote]
                        om_cv.save()

                        self.stdout.write("Person: %s - %s\n" % (om_charge.person.last_name.encode('utf8'), om_cv.vote))


                # update votation caches
                om_votation.update_caches()
                self.stdout.write("caches for this votation updated.\n")

    def handle(self, *labels, **options):

        if not labels:
            raise CommandError('Enter at least one %s.' % self.label)

        # parse people xml file into an lxml.etree
        people_file = options['people_file']
        if not path.isfile(people_file):
            raise IOError("File %s does not exist" % people_file)

        self.people_tree = etree.parse(people_file)

        # parse passed sittings
        for label in labels:
            self.handle_label(label, **options)
        return 'done\n'
