# -*- coding: utf-8 -*-
from optparse import make_option
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.management.base import LabelCommand, CommandError, BaseCommand

from lxml import etree
from os import path

from open_municipio.people.models import Institution, Person
from open_municipio.sittings.models import Sitting
from open_municipio.votations.models import Votation, ChargeVote, InstitutionCharge
from open_municipio import settings_import as settings

import logging



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
                    default='open_municipio/data_import/udine/votations/people.xml',
                    help='The xml file containing the persons'
        ),
    )

    args = "<filename filename ...>"
    help = "Import the voting information contained in the specified XML documents"
    label = 'filename'

    logger = logging.getLogger('import')

    people_tree = None

    def lookupCharge(self, om_id, **options):
        """
        look for the correct open municipio charge, or return None
        """
        people_charges = self.people_tree.xpath(
            '//om:Person[@om_id=%s]' % om_id,
            namespaces={'om': "http://www.openmunicipio.it"}
        )
        if len(people_charges) == 1:
            id = people_charges[0].get('id')
            if id is None:
                if int(options['verbosity']) > 0:
                    self.logger.error(" charge with om_id %s has no id in people XML file. Skipping.\n" % om_id)
                return None
            return id
        elif len(people_charges) > 1:
            if int(options['verbosity']) > 0:
                self.logger.error(" more than one person for om_id %s in people XML file. Skipping.\n" % om_id)
            return None
        else:
            if int(options['verbosity']) > 0:
                self.logger.error(" no person for om_id %s in people XML file. Skipping.\n" % om_id)
            return None


    def handle_label(self, filename, **options):
        if not path.isfile(filename):
            raise IOError("File %s does not exist" % filename)

        tree = etree.parse(filename)

        sittings = tree.xpath("/om:Sitting",namespaces=NS)
        self.logger.debug("%d Sittings to import\n" % len(sittings))
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
            self.logger.debug("Working in institution %s" % curr_inst)

            sitting_date = xml_sitting.get("date")[0:10]
            om_sitting, created = Sitting.objects.get_or_create(
                number=xml_sitting.get("num"),
                date=sitting_date,
                institution=curr_inst
            )

            if not created:
                self.logger.debug("Found sitting %s - %s" % (om_sitting.number, sitting_date))
            else:
                self.logger.debug("Created sitting %s - %s" % (om_sitting.number, sitting_date))

            # fetch all votations for the sitting in the XML
            votations = xml_sitting.xpath("./om:Votation", namespaces=NS)
            self.logger.debug("%d Votations to import\n" % len(votations))
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
                    self.logger.debug("Found votation %s\n" % om_votation.idnum)
                else:
                    self.logger.debug("Created votation %s\n" % om_votation.idnum)

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

                self.logger.debug("title: %s\n" % om_votation.act_descr.encode('utf-8'))

                # build a ChargeVote for every single vote
                chargevotes = xml_votation.xpath("./om:Votes/om:ChargeVote", namespaces=NS)
                self.logger.debug("Votation in XML contains %d ChargeVotes\n" % len(chargevotes))

                # loop over all members of the institution
                # at the time of the sitting
                for m in curr_inst.charge_set.current(as_of=sitting_date):
                    om_id = m.person.id
                    xml_id = self.lookupCharge(om_id)
                    self.logger.debug("Member: %s (om_id:%s => xml_id:%s)" % (m, om_id, xml_id ))
                    chargevote = xml_votation.xpath("./om:Votes/om:ChargeVote[@componentId=%s]" % xml_id, namespaces=NS)
                    if len(chargevote):
                        vote = chargevote[0].get('vote')
                        self.logger.debug("Vote: %s" % vote)
                    else:
                        self.logger.error("Absent!")

                """
                # remove all votes in this votation if overwriting
                if options['overwrite']:
                    ChargeVote.objects.filter (votation=om_votation).delete()

                for n, xml_cv in enumerate(chargevotes, start=1):
                    self.logger.debug(
                        "%s) ComponentId: %s " % (n, xml_cv.get('componentId'))
                    )
                    # lookup council charges to match with ChargeVote
                    om_charge = self.lookupCharge(xml_cv, council_inst, **options)
                    if om_charge is None:
                        self.logger.debug(
                            "charge not found. Skipping \n"
                        )
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

                        self.logger.debug("Person: %s - %s\n" % (om_charge.person.last_name.encode('utf8'), om_cv.vote))
                """

                # update votation caches
                om_votation.update_caches()
                self.logger.debug("caches for this votation updated.\n")

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
