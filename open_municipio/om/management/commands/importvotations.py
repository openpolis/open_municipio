from django.core.management.base import BaseCommand, CommandError

from lxml import etree
from os import path

from open_municipio.people.models import Sitting
from open_municipio.votations.models import Votation, ChargeVote, InstitutionCharge

import dateutil.parser
#from time import strptime
#import datetime
import sys, traceback
from open_municipio.settings_import import XML_TO_OM_INST, XML_TO_OM_VOTE, IMPORT_NS

class Command(BaseCommand):
    args = "<filename filename ...>"
    help = "Import the voting information contained in the specified XML documents"

    def lookupCharge(self, xml_chargevote):
        try:
            inst_pk = int(xml_chargevote.get("componentId"))
            om_charge = InstitutionCharge.objects.all().get(pk=inst_pk)
        except Exception,e:
            print("Exception lookingup charge: %s" % e)
            om_charge = None

        return om_charge

    def lookupChargeVote(self, om_charge, om_votation):
        om_chargevotes = ChargeVote.objects.filter(charge=om_charge,votation=om_votation)
        if len(om_chargevotes) == 0:
            return None
        if len(om_chargevotes) > 1:
            print("More than one ChargeVote for votation %d" % om_votation.pk)

        return om_chargevotes[0]

    def lookupVotation(self, xml_votation, om_sitting):
        vot_num = xml_votation.get("seq_n")
        if vot_num == None:
            raise Exception("Votation without 'seq_n' attribute not allowed")

        try:
            om_votation = Votation.objects.get(idnum=vot_num,
                sitting=om_sitting)
            return om_votation
        except Exception: # limit to DoesNotExist
            return None

    def lookupOrAddSitting(self, xml_sitting):
        sitt_num = xml_sitting.get("num")
        str_date = xml_sitting.get("date")
        sitt_date = dateutil.parser.parse(xml_sitting.get("date"))
        sitt_type = xml_sitting.get("type")

        if sitt_type == None or sitt_date == None or sitt_num == None:
            raise Exception("Sitting date,num and type must be provided. Passed, respectively: %s,%s,%s" % (sitt_num,sitt_date,sitt_type))

        print("Lookup sitting num %s, date %s, type %s" % (sitt_num,sitt_date,sitt_type))

# TODO unable to find institution
        curr_inst = XML_TO_OM_INST[sitt_type]

        sitting_QS = Sitting.objects.filter(number=sitt_num,date=sitt_date,institution=curr_inst)[:1]
    
#        if om_sitting == None:
        if sitting_QS:
            om_sitting = sitting_QS[0]
            print("Found sitting", om_sitting)
        else:
# add the sitting because not present
            om_sitting = Sitting()            
            om_sitting.number = sitt_num
            om_sitting.date = sitt_date
            om_sitting.institution = curr_inst
            om_sitting.save()
            print("Created sitting", om_sitting)

    def buildVotation(self, xml_votation, om_sitting):
        vot_num = xml_votation.get("seq_n")

        if vot_num == None:
            raise Exception("Votation without 'seq_n' attribute not allowed")

        print("Build OM Votation num %s" % vot_num)

        om_votation = Votation()
        om_votation.sitting = om_sitting
        om_votation.idnum = vot_num
        om_votation.act_descr = "" # TODO get it from the votation
#        om_votation.charge_set = None # TODO get it from the votation
        om_votation.n_legal = xml_votation.get("legal_number")
        om_votation.n_presents = xml_votation.get("presents")
        om_votation.n_yes = xml_votation.get("counter_yes")
        om_votation.n_no = xml_votation.get("counter_no")
        om_votation.n_abst = xml_votation.get("counter_abs")
# TODO majority not present in XML?
        om_votation.outcome = xml_votation.get("outcome") # decode
        return om_votation

    def buildChargeVote(self, xml_cv, om_charge, om_votation):
        print("Inside buildChargeVote")
        om_cv = ChargeVote()
        om_cv.votation = om_votation

        xml_vote = xml_cv.get("vote")
        if not (xml_vote in XML_TO_OM_VOTE):
            print("Cannot store ChargeVote. XML vote code '%d' not recognized" %
                xml_vote)
            return None
        om_cv.vote = XML_TO_OM_VOTE[xml_vote]

        om_cv.charge = om_charge
        return om_cv
       

    def handleFile(self, filename):
        if not path.isfile(filename):
            raise IOError("File %s does not exist" % filename)

        tree = etree.parse(filename)

        sittings = tree.xpath("/om:Sitting",namespaces=IMPORT_NS)
        print("%d Sittings to import" % len(sittings))
        for xml_sitting in sittings:
            om_sitting = self.lookupOrAddSitting(xml_sitting)

            votations = xml_sitting.xpath("./om:Votation", namespaces=IMPORT_NS)
            print("%d Votations to import" % len(votations))
            for xml_votation in votations:
                om_votation = self.lookupVotation(xml_votation, om_sitting)

                # if the Votation has already been imported, ignore it
                vot_num = xml_votation.get("seq_n")
                if om_votation != None:
                    print("Votation num %s already present" % vot_num)
                    continue
                
                # build one Votation for the entire votation
                om_votation = self.buildVotation(xml_votation, om_sitting)

                # build a ChargeVote for every single vote
                chargevotes = xml_votation.xpath("./om:Votes/om:ChargeVote",
                    namespaces=IMPORT_NS)
                print("Votation contains %d ChargeVotes" % len(chargevotes))
                for xml_cv in chargevotes:
                    om_charge = self.lookupCharge(xml_cv)

                    if om_charge == None:       
                        charge_pk = xml_cv.get("componentId")
                        print("InstitutionCharge (componentId=%s) not found, unable to import ChargeVote" % charge_pk)
                        continue
    
                    om_cv = self.lookupChargeVote(om_charge, om_votation)

                    if om_cv != None:
                        print("ChargeVote (charge pk=%s) already found for Votation (pk=%d)" % (om_cv.charge.pk, om_votation.pk))
                        continue;

                    om_cv = self.buildChargeVote(xml_cv, om_charge, om_votation)

                    if om_cv == None:
                        print("ChargeVote importation interrupted")
                        return
                    om_cv.save()
                    print("Saved ChargeVote", om_cv)
                

    def print_help(self):
        self.stdout.write("Command syntax:\n")
        self.stdout.write("importvotation %s\n" % self.args)
        self.stdout.write("%s\n" % self.help)

    def handle(self, *args, **options):
        try:
            if len(args) == 0:
                self.print_help()
                return

            for filename in args:
                self.handleFile(filename)
        except Exception as e:
            traceback.print_exc()
            raise CommandError("Error executing command: %s" % e)

