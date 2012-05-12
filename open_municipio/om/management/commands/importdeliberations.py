# -*- coding: utf-8 -*-
from optparse import make_option
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.management.base import LabelCommand, CommandError, BaseCommand

from lxml import etree
from os import path

from open_municipio.people.models import Sitting, Institution, Person, municipality
from open_municipio.acts.models import *

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
                    default='import_tmp/udine/acts/people.xml',
                    help='The xml file containing the persons'
        ),
        )

    args = "<filename filename ...>"
    help = "Import the deliberation(s) contained in the specified XML document(s)"
    label = 'filename'

    people_tree = None

    def lookupCharge(self, xml_chargexref, institution=None):
        """
        look for the correct open municipio charge, or return None
        """
        XLINK_NAMESPACE = NS['xlink']
        XLINK = "{%s}" % XLINK_NAMESPACE
        try:
            file, charge_id = xml_chargexref.get(XLINK+"href").split("#")
            people_charges = self.people_tree.xpath(
                '//om:Person[@id="%s"]' % charge_id,
                namespaces=NS
            )
            if len(people_charges):
                om_id = people_charges[0].get('om_id')
                if om_id is None:
                    self.stderr.write("Warning: charge with id %s has no om_id (past charge?). Skipping.\n" % charge_id)
                    return None
                charge_type = people_charges[0].get('charge')
                if charge_type is None:
                    self.stderr.write("Warning: charge with id %s has no charge attribute. Skipping.\n" % charge_id)
                    return None

                # institution is grabbed from charge attribute, in acts import
                # since mayor and deputies may sign acts, not only counselor
                if charge_type == 'counselor':
                    institution = municipality.council.as_institution
                elif charge_type == 'deputy' or charge_type == 'firstdeputy':
                    institution = municipality.gov.as_institution
                elif charge_type == 'mayor':
                    institution = municipality.mayor.as_institution
                else:
                    self.stderr.write("Warning: charge with id %s has wrong charge attribute %s. Skipping.\n" %
                                      (charge_id, charge_type))
                    return None

                try:
                    person = Person.objects.get(pk=int(om_id))
                    charge =  person.current_institution_charge(institution)
                    return charge
                except ObjectDoesNotExist:
                    self.stderr.write("Warning: could not find person or charge for id = %s in open municipio DB. Skipping.\n" % charge_id)
                    return None
                except MultipleObjectsReturned:
                    self.stderr.write("Error: found more than one person or charge for id %s in open municipio db. Skipping.\n" % charge_id)
                    return None
            else:
                self.stderr.write("Warning: could not find person for id %s in peopkle XML file. Skipping.\n" % charge_id)
                return None
        except ObjectDoesNotExist:
            self.stderr.write("Warning: could not find charge with id %s in Open Municipio DB. Skipping.\n" % component_id)
            return None


    def handle_label(self, filename, **options):
        if not path.isfile(filename):
            raise IOError("File %s does not exist" % filename)

        tree = etree.parse(filename)

        acts = tree.xpath("/om:CouncilDeliberation",namespaces=NS)
        self.stdout.write("%d Acts to import\n" % len(acts))
        for xml_act in acts:

            # get important attributes
            id = xml_act.get("id")
            if id is None:
                self.stderr.write(
                    "Error: Act has no id attribute! Skipping this sitting."
                )
                continue

            initiative = settings.XML_TO_OM_INITIATIVE[xml_act.get("initiative")]
            if initiative is None:
                self.stderr.write(
                    "Error: Act %s has no initiative attribute! Skipping this sitting." % id
                )
                continue
            # transform xml value into database string
            initiative = Deliberation.INITIATIVE_CHOICES.__dict__['_choice_dict'][initiative]

            presentation_date = xml_act.get("presentation_date")
            if presentation_date is None:
                self.stderr.write(
                    "Error: Act %s has no presentation_date attribute! Skipping this sitting." % id
                )
                continue
            pd = "%s-%s-%s" %\
                (presentation_date[0:4],
                 presentation_date[4:6],
                 presentation_date[6:8])

            title = xml_act.get("title")
            if title is None:
                self.stderr.write(
                    "Error: Act %s has no title attribute! Skipping this sitting." % id
                )
                continue

            final_id = xml_act.get('final_id')


            # get or create the deliberation object
            curr_inst = municipality.council.as_institution
            om_act, created = Deliberation.objects.get_or_create(
                idnum=id,
                presentation_date=pd,
                emitting_institution=curr_inst,
                initiative=initiative,
                title=title
            )

            if not created:
                self.stdout.write("Found deliberation %s\n" % om_act.idnum)
            else:
                self.stdout.write("Created deliberation %s\n" % om_act.idnum)

            # fetch all subscribers for the act in the XML
            subscribers = xml_act.xpath("./om:ActSubscribers", namespaces=NS)
            self.stdout.write("%d Subscribers sets to import\n" % len(subscribers))
            for xml_subscribers_set in subscribers:

                support_type = xml_subscribers_set.get("type")
                if support_type is None:
                    self.stderr.write(
                        "ActSubscriber has no type attribute! Skipping it."
                    )
                    continue
                # TODO: modify support_type from xml (first_signer and co_signer)
                if support_type == 'first_subscriber':
                    support_type = ActSupport.SUPPORT_TYPE.first_signer
                else:
                    support_type = ActSupport.SUPPORT_TYPE.co_signer

                # remove all act supports of this type
                # TODO: overwrite?
                # ActSupport.objects.filter(act=om_act, support_type=type).delete()

                # build a ChargeVote for every single vote
                chargexrefs = xml_subscribers_set.xpath("./om:ChargeXRef", namespaces=NS)
                self.stdout.write("ActSubscriber contains %d ChargeXRefs\n" % len(chargexrefs))
                for xml_chargexref in chargexrefs:
                    om_charge = self.lookupCharge(xml_chargexref, curr_inst)

                    # add act support for this charge
                    om_as, created = ActSupport.objects.get_or_create(
                        charge=om_charge,
                        act=om_act,
                        support_type=support_type
                    )

                    # todo, modify XML to add support date
                    #if date is not specified, get it from act
                    om_as.date=om_act.presentation_date
                    om_as.save()


            # remove all act attachments of this type
            # TODO: overwrite?
            # Attach.objects.filter(act=om_act, title=title).delete()

            # fetch all attachments for the act in the XML
            attachments = xml_act.xpath("./om:Attachment", namespaces=NS)
            self.stdout.write("%d Attachments to import\n" % len(attachments))
            for xml_attach in attachments:

                attach_title = xml_attach.xpath("./om:AttachDescription")
                if attach_title is None:
                    self.stderr.write(
                        "Error: Act %s has no description! Skipping this sitting." % id
                    )
                    continue

                attach_type = xml_attach.get("type")
                if attach_type is None:
                    self.stderr.write(
                        "Attachment has no type attribute! Skipping it."
                    )
                    continue


                # build a new attach
                # TODO: file upload
                om_att, created = Attach.objects.get_or_create(
                    act=om_act,
                    type=attach_type,
                    title=attach_title
                )
                om_att.document_date = om_act.presentation_date
                om_att.save()

            # call parent class save to trigger
            # real-time search index update
            # since signals do not handle hierarchy well
            om_act.act_ptr.save()

    def handle(self, *labels, **options):
        if not labels:
            raise CommandError('Enter at least one %s.' % self.label)

        # parse people xml file into an lxml.etree
        people_file = options['people_file']
        if not path.isfile(people_file):
            raise IOError("File %s does not exist" % people_file)

        self.people_tree = etree.parse(people_file)

        # parse passed acts
        for label in labels:
            self.handle_label(label, **options)
        return 'done\n'
