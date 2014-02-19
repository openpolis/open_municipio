# -*- coding: utf-8 -*-
from optparse import make_option
import os
import re
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.management.base import LabelCommand, CommandError, BaseCommand
from django.core.files import File

from lxml import etree, html
from os import path

from haystack.backends.solr_backend import SolrSearchBackend
from pysolr import SolrError
from open_municipio.people.models import Person, municipality
from open_municipio.acts.models import *

import logging

from open_municipio.data_import import conf

# configure xml namespaces
NS = {
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'om': 'http://www.openmunicipio.it',
    'xlink': 'http://www.w3.org/1999/xlink'
}
XLINK_NAMESPACE = NS['xlink']
XLINK = "{%s}" % XLINK_NAMESPACE

class ImportVotationsCommand(LabelCommand):
    option_list = BaseCommand.option_list + (
        make_option('--people-file',
                    dest='people_file',
                    default="people.xml",
                    help='The xml file containing the persons ids mappings'
        ),
        make_option('--dry-run',
                    action='store_true',
                    dest='dry_run',
                    default=False,
                    help='Execute without actually writing into the DB'
        ),
    )

    args = "<filename filename ...>"
    help = "Import the votation(s) contained in the specified MDB file(s)."
    label = 'filename'

    dry_run = False

    logger = logging.getLogger('import')

    people_tree = None

    def handle_label(self, filename, **options):
        raise Exception("Not implemented")

    def handle(self, *labels, **options):
        if not labels:
            raise CommandError('Enter at least one %s.' % self.label)

        # parse people xml file into an lxml.etree
        people_file = options['people_file']
        if not path.isfile(people_file):
            raise IOError("File %s does not exist" % people_file)

        self.people_tree = etree.parse(people_file)

        self.dry_run = options['dry_run']

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


        # parse passed votations
        for label in labels:
            self.handle_label(label, **options)
        return 'done'


class ImportActsCommand(LabelCommand):
    option_list = BaseCommand.option_list + (
        make_option('--people-file',
                    dest='people_file',
                    default=conf.ACTS_PEOPLE_FILE,
                    help='The xml file containing the persons ids mappings'
        ),
        make_option('--act-type',
                    dest='act_type',
                    default='CouncilDeliberation',
                    help='The type of act to import (CouncilDeliberation, Motion, Interrogation)'
        ),
        make_option('--dry-run',
                    action='store_true',
                    dest='dry_run',
                    default=False,
                    help='Execute without actually writing into the DB'
        ),
        make_option('--refresh-news',
                    action='store_true',
                    dest='refresh_news',
                    default=False,
                    help='Remove news related to an act, before importing it. News are re-created.'
        ),
        make_option('--rewrite-signatures',
                    action='store_true',
                    dest='rewrite_signatures',
                    default=False,
                    help="Remove act's presenters before importing."
        ),
        make_option('--from-date',
                    dest='from_date',
                    default=None,
                    help="Date interval start (beginning of consiliatura)"
        ),
        make_option('--to-date',
                    dest='to_date',
                    default=None,
                    help="Date interval end (end of consiliatura)"
        ),
    )

    args = "<filename filename ...>"
    help = "Import the act(s) of type act_type, contained in the specified XML document(s)."
    label = 'filename'

    dry_run = False

    logger = logging.getLogger('import')

    people_tree = None

    def lookupCharge(self, xml_chargexref, institution=None, moment=None):
        """
        look for the correct open municipio charge, or return None
        if the date parameter is not passed, then current charges are looked up
        """
        try:
            file, charge_id = xml_chargexref.get(XLINK+"href").split("#")
            people_charges = self.people_tree.xpath(
                '//om:Person[@id="%s"]' % charge_id,
                namespaces=NS
            )
            if len(people_charges):
                om_id = people_charges[0].get('om_id')
                if om_id is None:
                    self.logger.warning("charge with id %s has no om_id (past charge?). Skipping." % charge_id)
                    return None
                charge_type = people_charges[0].get('charge')
                if charge_type is None:
                    self.logger.warning("charge with id %s has no charge attribute. Skipping." % charge_id)
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
                    self.logger.error("Warning: charge with id %s has wrong charge attribute %s. Skipping." %
                                      (charge_id, charge_type))
                    return None

                try:
                    person = Person.objects.get(pk=int(om_id))
                    charge = person.get_current_charge_in_institution(institution, moment=moment)
                    self.logger.debug("id %s (%s) mapped to %s (%s)" %
                                      (charge_id, charge_type, person, charge))
                    return charge
                except ObjectDoesNotExist:
                    self.logger.warning("could not find person or charge for id = %s in open municipio DB. Skipping." % charge_id)
                    return None
                except MultipleObjectsReturned:
                    self.logger.error("found more than one person or charge for id %s in open municipio db. Skipping." % charge_id)
                    return None
            else:
                self.logger.warning("could not find person for id %s in people XML file. Skipping." % charge_id)
                return None
        except ObjectDoesNotExist:
            self.logger.warning("could not find charge for %s in Open Municipio DB. Skipping." % xml_chargexref)
            return None

    def fetch_signers(self, om_act, xml_subscribers_set, support_type, charge_lookup_institution):
        """
        extract signers from an om:ActSubscribers tag and build related ActSupport records
        om_act - the Act instance supported
        xml_subscribers_set - the om:ActSubscribers xml node
        support_type - the type of support (first_signer, co_signer)
        """

        # build an ActSupport for every single charge
        supports = xml_subscribers_set.xpath("./om:ActSupport", namespaces=NS)
        self.logger.info(" ActSubscriber contains %d ActSupports" % len(supports))
        for xml_support in supports:
            support_date = xml_support.get("date")
            # if date is not specified, get it from act's presentation date
            if support_date is None:
                support_date = str(om_act.presentation_date)
            chargexref = xml_support.xpath("./om:ChargeXRef", namespaces=NS)[0]
            om_charge = self.lookupCharge(chargexref, charge_lookup_institution, moment=support_date)
            if om_charge is None:
                continue

            # add act support for this charge
            om_as, created = ActSupport.objects.get_or_create(
                charge=om_charge,
                act=om_act,
                support_type=support_type
            )

            # always rewrite support date
            om_as.support_date = support_date

            if not self.dry_run:
                om_as.save()

    def fetch_attachments(self, filename, om_act, xml_act):
        """
        fetch all attachments for the act in the XML
        om_act - related Act instance
        xml_act - act xml node
        """

        attachments = xml_act.xpath("./om:Attachment", namespaces=NS)
        self.logger.info("%d Attachments to import" % len(attachments))
        for xml_attach in attachments:

            attach_title = xml_attach.get("title")
            if attach_title is None:
                self.stderr.write(
                    "Error: Attach has no title! Skipping this sitting." % id
                )
                continue

            attach_href = xml_attach.get(XLINK+"href")
            if attach_href is None:
                self.stderr.write(
                    "Attachment has no xlink:href attribute! Skipping it."
                )
                continue

            attach_dir = attach_href.split('/')[-2]
            attach_file = path.join(path.dirname(filename), attach_href).encode('utf8')
            if not path.isfile(attach_file):
                self.stderr.write("File %s does not exist. Skipping!\n" % attach_file)
                continue

            # build a new attach only if old is not found
            om_att, created = Attach.objects.get_or_create(
                act=om_act,
                title=attach_title
            )
            om_att.document_date = om_act.presentation_date
            if not self.dry_run:
                om_att.save()

            # remove old attach file to avoid _1 files whenb rewriting
            if not self.dry_run:
                try:
                    old_attach_file = om_att.file.file
                    os.remove(old_attach_file.name)
                except ValueError:
                    pass
                except IOError:
                    pass

            # overwrite attach file and save it under media (/uploads)
            attach_filename = path.basename(attach_file)
            attach_f = open(attach_file, 'r')

            if not self.dry_run:
                try:
                    om_att.file.save("%s_%s" % (attach_dir, attach_filename.decode('utf8')), File(attach_f))
                except UnicodeDecodeError:
                    self.logger.error("Could not save attachment with unicode characters: %s. Skipping." % (attach_filename,))

            om_att.document_type = os.path.splitext(attach_filename)[1][1:]
            om_att.document_size = File(attach_f).size
            self.logger.info(" will attach %s" % (attach_file, ))
            if not self.dry_run:
                om_att.save()

            # text extraction (using tika inside solr)
            if 'testoproposta' in attach_filename.lower() or\
               'testodiscussione' in attach_filename.lower():

                """
                Streamlines content extraction from a doc (pdf, or other format file, as specified in Tika) within a solr request.
                Requires Haystack 2.0.0.
                Handles unicode characters, as well.

                In settings, define this hash:
                HAYSTACK_CONNECTIONS = {
                    'default': {
                        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
                        'URL': 'http://127.0.0.1:8983/solr',
                        'TIMEOUT': 60 * 5,
                        'BATCH_SIZE': 100,
                        'SEARCH_RESULTS_PER_PAGE': 10,
                    }
                }


                from django.conf import settings
                from haystack.backends.solr_backend import SolrSearchBackend
                from lxml import html

                file_path = '/Users/guglielmo/Workspace/open_municipio/test_data/acts/20120622_ATTI_2008/DC_2008401100013/TestoProposta.doc'
                solr_backend = SolrSearchBackend('default', **settings.HAYSTACK_CONNECTIONS['default'])

                attach_f = open(file_path)
                file_content = solr_backend.extract_file_contents(attach_f)
                html_content = html.fromstring(file_content['contents'].encode('utf-8'))
                document_text = html_content.cssselect('body')[0].text_content()

                print document_text
                """


                # reset attach file pointer
                attach_f.seek(0)

                # text extraction, through haystack-solr and lxml.html
                solr_backend = SolrSearchBackend('default', **settings.HAYSTACK_CONNECTIONS['default'])

                try:
                    file_content = solr_backend.extract_file_contents(attach_f)

                    if file_content is None:
                        self.logger.error("  could not extract textual content from file, with solr-tika; skipping")
                        attach_f.close()
                        continue

                    html_content = html.fromstring(file_content['contents'].encode('utf-8'))
                    document_text = html_content.cssselect('body')[0].text_content()

                    self.logger.info("  textual content extracted from file")

                    # text content saved into attachment's text
                    om_att.text = document_text
                    if not self.dry_run:
                        om_att.save()

                    # for proposale, text content goes into act's content field
                    if 'testoproposta' in attach_filename.lower():
                        self.logger.info("  textual version of proposal added to act")
                        om_act.text = document_text
                        if not self.dry_run:
                            om_act.save()
                except SolrError:
                    self.logger.warning("  could not extract textual content with solr-tika")

                attach_f.close()

    def fetch_transitions(self, transitions_map, om_act, xml_act):
        """
        Fetch transitions from XML and map them to possible act statuses,
        creating and connecting them to the act when non-existent.
        Existing transitions are over-writtem.
        """
        # get transitions from xml tree
        transitions = xml_act.xpath("./om:CouncilDeliberationTransition", namespaces=NS)
        self.logger.info("%d Transisions to import" % len(transitions))

        for xml_transition in transitions:
            # read name attribute
            transition_name = xml_transition.get("name").lower()
            if transition_name is None:
                self.logger.error(
                    "Transition has no name attribute! Skipping it."
                )
                continue
            # map name into status
            if not transition_name in transitions_map:
                self.logger.debug(
                    "Transition {0} not found! Skipping it.".format(transition_name)
                )
                continue
            transition_status = transitions_map[transition_name]
            # read date attribute
            transition_date = xml_transition.get("date")
            if transition_date is None:
                self.logger.error(
                    "Transition has no date attribute! Skipping it."
                )
                continue

            # add or read transition status for this act
            trans, created = om_act.transition_set.get_or_create(
                act=om_act.act_ptr,
                final_status=transition_status,
                defaults={
                    'transition_date': transition_date,
                }
            )

            # overwrite date and status of an existing transition
            if not created:
                trans.transition_date = transition_date
                trans.final_status = transition_status
                trans.save()


    def remove_news(self, act):
        """
        if required by the --refresh-news options, related news are removed
        i.e., all news having related_object of type
           Act (act)
           Transition with t in act.transition_set.all(), and
           ActSupport with s in act.actsupport_set.all()
        """

        # remove news related to om_act
        act.related_news.delete()
        self.logger.debug("  news related to act removed")

        # remove news generated by ActSupport originated by om_act
        # this removes the news regarding the politician
        News.objects.filter(
            generating_object_pk__in=act.actsupport_set.values('id'),
            generating_content_type=ContentType.objects.get_for_model(ActSupport)
        ).delete()
        self.logger.debug("  news generated by ActSupport removed")

    def handle_deliberation(self, filename, **options):
        """
        handles both council deliberation and city government deliberation parsing
        """

        # get act type: CouncilDeliberation or CGDeliberation
        act_type = options['act_type']
        if act_type == 'CouncilDeliberation':
            deliberation_tag = "/om:CouncilDeliberation"
            initiative_types = Deliberation.INITIATIVE_TYPES
            deliberation_manager = Deliberation.objects
            emitting_institution = municipality.council.as_institution
        else:
            deliberation_tag = "/om:CityGovernmentDeliberation"
            initiative_types = CGDeliberation.INITIATIVE_TYPES
            deliberation_manager = CGDeliberation.objects
            emitting_institution = municipality.gov.as_institution

        try:
            tree = etree.parse(filename)
        except etree.XMLSyntaxError:
            self.logger.error("Syntax error while parsing %s. Skipping." % (filename,))
            return

        acts = tree.xpath(deliberation_tag, namespaces=NS)
        self.logger.info("%d Deliberation to import" % len(acts))
        for xml_act in acts:

            id = xml_act.get("id")
            if id is None:
                self.logger.error(
                    "Error: Act has no id attribute! Skipping."
                )
                continue

            presentation_date = xml_act.get("presentation_date")
            if presentation_date is None:
                self.logger.error(
                    "Error: Act %s has no presentation_date attribute! Skipping." % id
                )
                continue

            # check if presentation date is in range
            if not self._check_presentation_date(presentation_date):
                self.logger.error(
                    "Error: Act %s has presentation_date (%s) out of required range %s - %s! Skipping." %
                    (id, presentation_date, self.date_start, self.date_end)
                )
                continue

            # get important attributes
            initiative = conf.XML_TO_OM_INITIATIVE[xml_act.get("initiative")]
            if initiative is None:
                self.logger.error(
                    "Error: Act %s has no initiative attribute! Skipping." % id
                )
                continue
                # transform xml value into database string
            initiative = initiative_types._choice_dict[initiative]


            title = xml_act.xpath("./om:Title", namespaces=NS)
            if title is None:
                self.logger.error(
                    "Error: Act %s has no title attribute! Skipping." % id
                )
                continue
            title = title[0].text

            approval_date = xml_act.get("approval_date")
            execution_date = xml_act.get("execution_date")
            final_idnum = xml_act.get("final_id")

            logger.debug("Final idnum: %s" % final_idnum)

            # get or create the deliberation object
            # the dynamic deliberation_manager allows to create different Deliberation instances
            om_act, created = deliberation_manager.get_or_create(
                idnum=id,
                presentation_date=presentation_date,
                emitting_institution=emitting_institution,
                initiative=initiative,
                defaults={
                    'title':title,
                    'approval_date': approval_date,
                    'execution_date': execution_date,
                    'final_idnum': final_idnum
                }
            )

            if not created:
                self.logger.info("Found %s %s" % (act_type, om_act.idnum))

                if title != om_act.title:
                    self.logger.info("Title changed: %s" % om_act.title)
                    om_act.title = title

                # remove news of an existing act, if required
                if options['refresh_news']:
                    self.remove_news(om_act)

                # always override approval_date, execution_date and final_idnum
                # if passed in the xml
                if approval_date:
                    om_act.approval_date = approval_date
                if execution_date:
                    om_act.excution_date = execution_date
                if final_idnum:
                    om_act.final_idnum = final_idnum

                #save act and finalize db transitions
                om_act.save()
            else:
                self.logger.info("Created %s %s" % (act_type, om_act.idnum))


            if options['rewrite_signatures'] and not options['dry_run']:
                om_act.actsupport_set.all().delete()

            # fetch all subscribers for the act in the XML
            subscribers = xml_act.xpath("./om:ActSubscribers", namespaces=NS)
            self.logger.info("%d Subscribers sets to import" % len(subscribers))
            for xml_subscribers_set in subscribers:

                # check that support type exists (for deliberations)
                support_type = xml_subscribers_set.get("type")
                if support_type is None:
                    self.logger.error(
                        "ActSubscriber has no type attribute! Skipping it."
                    )
                    continue

                # map xml support types to ours (first_signer and co_signer)
                if support_type == 'first_subscriber':
                    support_type = ActSupport.SUPPORT_TYPE.first_signer
                else:
                    support_type = ActSupport.SUPPORT_TYPE.co_signer

                self.fetch_signers(om_act, xml_subscribers_set, support_type, emitting_institution)


            # add presentation transition
            # after signatures, so that presentation news can be shortened
            if om_act.presentation_date is not None:

                # create transition: act is presented
                created = False
                trans, created = om_act.transition_set.get_or_create(
                    act=om_act.act_ptr,
                    final_status=om_act.STATUS.presented,
                    defaults={
                        'transition_date': om_act.presentation_date,
                    }
                )
                if created:
                    logger.debug("  presentation transition created")
                else:
                    logger.debug("  presentation transition found")
                    trans.transition_date = om_act.presentation_date
                    trans.save()
            else:
                logger.debug("  presentation transition can't be added, no presentation_date")

            # fetch transitions statuses
            self.fetch_transitions(self.TRANSITION_STATUS_MAP_DEL, om_act, xml_act)

            # create approval transition for Deliberations, if approval_date is defined
            if om_act.approval_date is not None:
                trans, created = om_act.transition_set.get_or_create(
                    act=om_act.act_ptr,
                    final_status=om_act.STATUS.approved,
                    defaults={
                        'transition_date': om_act.approval_date,
                    }
                )
                if created:
                    logger.debug("  approval transition created")
                else:
                    logger.debug("  approval transition found")
                    trans.transition_date = om_act.approval_date
                    trans.save()



            self.fetch_attachments(filename, om_act, xml_act)

            # call parent class save to trigger
            # real-time search index update
            # since signals do not handle hierarchy well
            if not self.dry_run:
                if om_act.text:
                    om_act.act_ptr.text = om_act.text
                om_act.act_ptr.save()

    def handle_interrogation(self, filename, **options):

        try:
            tree = etree.parse(filename)
        except etree.XMLSyntaxError:
            self.logger.error("Syntax error while parsing %s. Skipping." % (filename,))
            return

        acts = tree.xpath("/om:Interrogation",namespaces=NS)
        self.logger.info("%d Interrogations/Interpellations to import" % len(acts))
        for xml_act in acts:

            # get important attributes
            id = xml_act.get("id")
            if id is None:
                self.stderr.write(
                    "Error: Act has no id attribute! Skipping this sitting."
                )
                continue

            presentation_date = xml_act.get("presentation_date")
            if presentation_date is None:
                self.stderr.write(
                    "Error: Act %s has no presentation_date attribute! Skipping this sitting." % id
                )
                continue

            # check if presentation date is in range
            if not self._check_presentation_date(presentation_date):
                self.logger.error(
                    "Error: Act %s has presentation_date (%s) out of required range %s - %s! Skipping." %
                    (id, presentation_date, self.date_start, self.date_end)
                )
                continue

            answer_type = xml_act.get("answer_type")
            if answer_type is None:
                self.stderr.write(
                    "Error: Act %s has no answer_type attribute! Skipping this sitting." % id
                )
                continue

            title = xml_act.xpath("./om:Title", namespaces=NS)
            if title is None:
                self.stderr.write(
                    "Error: Act %s has no title attribute! Skipping this sitting." % id
                )
                continue
            title = title[0].text

            if re.match("interpellanza\s.*", title.lower()):
                # get or create the interrogation object
                curr_inst = municipality.council.as_institution
                om_act, created = Interpellation.objects.get_or_create(
                    idnum=id,
                    presentation_date=presentation_date,
                    emitting_institution=curr_inst,
                    answer_type=answer_type,
                    defaults = {
                        'title':title,
                        }
                )
                if not created:
                    self.logger.info("Found interpellation %s" % om_act.idnum)

                    if title != om_act.title:
                        self.logger.info("Title changed: %s" % om_act.title)
                        om_act.title = title

                    # remove news if required
                    if options['refresh_news']:
                        self.remove_news(om_act)

                    #save act and finalize db transitions
                    om_act.save()
                else:
                    self.logger.info("Created interpellation %s" % om_act.idnum)
            else:
                # get or create the interrogation object
                curr_inst = municipality.council.as_institution
                om_act, created = Interrogation.objects.get_or_create(
                    idnum=id,
                    presentation_date=presentation_date,
                    emitting_institution=curr_inst,
                    answer_type=answer_type,
                    defaults = {
                        'title':title,
                    }
                )
                if not created:
                    self.logger.info("Found interrogation %s" % om_act.idnum)

                    if title != om_act.title:
                        self.logger.info("Title changed: %s" % om_act.title)
                        om_act.title = title

                    # remove news if required
                    if options['refresh_news']:
                        self.remove_news(om_act)

                    #save act and finalize db transitions
                    om_act.save()
                else:
                    self.logger.info("Created interrogation %s" % om_act.idnum)

            if options['rewrite_signatures'] and not options['dry_run']:
                om_act.actsupport_set.all().delete()

            # fetch all subscribers for the act in the XML
            subscribers = xml_act.xpath("./om:ActSubscribers", namespaces=NS)
            self.logger.info("%d Subscribers sets to import" % len(subscribers))
            for xml_subscribers_set in subscribers:

                # support type for interrogations are always first_signer
                support_type = ActSupport.SUPPORT_TYPE.first_signer

                #fetch signers for the subscribers set
                self.fetch_signers(om_act, xml_subscribers_set, support_type, curr_inst)


            # add presentation transition
            # after signatures, so that presentation news can be shortened
            if om_act.presentation_date is not None:

                # create transition: act is presented
                created = False
                trans, created = om_act.transition_set.get_or_create(
                    act=om_act.act_ptr,
                    final_status=om_act.STATUS.presented,
                    defaults = {
                        'transition_date': om_act.presentation_date,
                    }
                )
                if created:
                    logger.debug("  presentation transition created")
                else:
                    logger.debug("  presentation transition found")
                    trans.transition_date = om_act.presentation_date
                    trans.save()
            else:
                logger.debug("  presentation transition can't be added, no presentation_date")

            # fetch transitions statuses
            self.fetch_transitions(self.TRANSITION_STATUS_MAP_INT, om_act, xml_act)



            self.fetch_attachments(filename, om_act, xml_act)

            # call parent class save to trigger
            # real-time search index update
            # since signals do not handle hierarchy well
            if not self.dry_run:
                if om_act.text:
                    om_act.act_ptr.text = om_act.text
                om_act.act_ptr.save()

    def handle_motion(self, filename, **options):

        try:
            tree = etree.parse(filename)
        except etree.XMLSyntaxError:
            self.logger.error("Syntax error while parsing %s. Skipping." % (filename,))
            return

        acts = tree.xpath("/om:Motion",namespaces=NS)
        self.logger.info("%d Motions to import" % len(acts))
        for xml_act in acts:

            # get important attributes
            id = xml_act.get("id")
            if id is None:
                self.stderr.write(
                    "Error: Act has no id attribute! Skipping this sitting."
                )
                continue

            presentation_date = xml_act.get("presentation_date")
            if presentation_date is None:
                self.stderr.write(
                    "Error: Act %s has no presentation_date attribute! Skipping this sitting." % id
                )
                continue

            # check if presentation date is in range
            if not self._check_presentation_date(presentation_date):
                self.logger.error(
                    "Error: Act %s has presentation_date (%s) out of required range %s - %s! Skipping." %
                    (id, presentation_date, self.date_start, self.date_end)
                )
                continue

            title = xml_act.xpath("./om:Title", namespaces=NS)
            if title is None:
                self.stderr.write(
                    "Error: Act %s has no title attribute! Skipping this sitting." % id
                )
                continue
            title = title[0].text


            # get or create the interrogation object
            curr_inst = municipality.council.as_institution
            om_act, created = Motion.objects.get_or_create(
                idnum=id,
                presentation_date=presentation_date,
                emitting_institution=curr_inst,
                defaults = {
                    'title':title,
                }
            )

            if not created:
                self.logger.info("Found motion %s" % om_act.idnum)

                if title != om_act.title:
                    self.logger.info("Title changed: %s" % om_act.title)
                    om_act.title = title

                # remove news if required
                if options['refresh_news']:
                    self.remove_news(om_act)

                #save act and finalize db transitions
                om_act.save()

            else:
                self.logger.info("Created motion %s" % om_act.idnum)

            if options['rewrite_signatures'] and not options['dry_run']:
                om_act.actsupport_set.all().delete()

            # fetch all subscribers for the act in the XML
            subscribers = xml_act.xpath("./om:ActSubscribers", namespaces=NS)
            self.logger.info("%d Subscribers sets to import" % len(subscribers))
            for xml_subscribers_set in subscribers:

                # support type for interrogations are always first_signer
                support_type = ActSupport.SUPPORT_TYPE.first_signer

                #fetch signers for the subscribers set
                self.fetch_signers(om_act, xml_subscribers_set, support_type, curr_inst)


            # add presentation transition
            # after signatures, so that presentation news can be shortened
            if om_act.presentation_date is not None:

                # create transition: act is presented
                created = False
                trans, created = om_act.transition_set.get_or_create(
                    act=om_act.act_ptr,
                    final_status=om_act.STATUS.presented,
                    defaults={
                        'transition_date': om_act.presentation_date,
                    }
                )
                if created:
                    logger.debug("  presentation transition created")
                else:
                    logger.debug("  presentation transition found")
                    trans.transition_date = om_act.presentation_date
                    trans.save()
            else:
                logger.debug("  presentation transition can't be added, no presentation_date")

            # fetch transitions statuses
            self.fetch_transitions(self.TRANSITION_STATUS_MAP_MOT, om_act, xml_act)

            self.fetch_attachments(filename, om_act, xml_act)


            # call parent class save to trigger
            # real-time search index update
            # since signals do not handle hierarchy well
            if not self.dry_run:
                if om_act.text:
                    om_act.act_ptr.text = om_act.text
                om_act.act_ptr.save()

    def handle_label(self, filename, **options):
        if not path.isfile(filename):
            raise IOError("File %s does not exist" % filename)

        act_type = options['act_type']

        if act_type == 'CouncilDeliberation' or act_type == 'CGDeliberation':
            self.handle_deliberation(filename, **options)
        elif act_type == 'Interrogation':
            self.handle_interrogation(filename, **options)
        elif act_type == 'Motion':
            self.handle_motion(filename, **options)
        else:
            raise IOError("Act type %s not known" % options['act_type'])

    def handle(self, *labels, **options):
        if not labels:
            raise CommandError('Enter at least one %s.' % self.label)

        # parse people xml file into an lxml.etree
        people_file = options['people_file']
        if not path.isfile(people_file):
            raise IOError("File %s does not exist" % people_file)

        if options['refresh_news'] and options['dry_run']:
            raise CommandError("refresh-news and dry-run cannot be specified together")

        self.people_tree = etree.parse(people_file)

        self.dry_run = options['dry_run']

        self.date_start = options['from_date']
        self.date_end = options['to_date']

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

        # parse passed acts
        for label in labels:
            self.handle_label(label, **options)
        return 'done\n'


    def _check_presentation_date(self, presentation_date):
        """
        If date_start or date_end have been specified,
        check if the presentation date is within the range.
        """
        if self.date_start and presentation_date < self.date_start:
            return False
        if self.date_end and presentation_date > self.date_end:
            return False
        return True
