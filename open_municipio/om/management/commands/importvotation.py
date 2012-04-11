from django.core.management.base import BaseCommand, CommandError

from lxml import etree
from os import path

from open_municipio.people.models import Sitting
from open_municipio.votations.models import Votation, ChargeVote

import sys, traceback
from open_municipio.settings_import import XML_TO_OM_INST

class Command(BaseCommand):
    args = "<filename filename ...>"
    help = "Import the voting information contained in the specified XML documents"
    NS = {"om" : "http://www.openmunicipio.it",
            "xsi" : "http://www.w3.org/2001/XMLSchema-instance",
            "xlink" : "http://www.w3.org/1999/xlink" }

    def lookupSitting(self, *args, **options):
        sitt_num = options["sitt_num"]
        sitt_date = options["sitt_date"]
        sitt_type = options["sitt_type"]

# TODO unable to find institution
        curr_inst = XML_TO_OM_INST[sitt_type]

        sitting_QS = Sitting.objects.filter(number=sitt_num,date=sitt_date,institution=curr_inst)[:1]
    
#        if om_sitting == None:
        if sitting_QS:
            om_sitting = sitting_QS[0]
        else:
# add the sitting because not present
            om_sitting = Sitting()            
            om_sitting.number = sitt_num
            om_sitting.date = sitt_date
            om_sitting.institution = curr_inst
            om_sitting.save()

    def handleFile(self, *args, **kwargs):
        if not("filename" in kwargs):
            raise CommandError("You must specify a 'filename' paramenter")
        filename = kwargs["filename"]

        if not path.isfile(filename):
            raise IOError("File %s does not exist" % filename)

        tree = etree.parse(filename)

        sittings = tree.xpath("/om:Sitting",namespaces=self.NS)
        print("%d Sittings to import" % len(sittings))
        for xml_sitting in sittings:
            sitt_num = xml_sitting.get("num")
            sitt_date = xml_sitting.get("date")

            print("Import sitting num %s, date %s" % (sitt_num,sitt_date))

# do not consider call

            om_sitting = self.lookupSitting(sitt_num=sitt_num,
                sitt_date=sitt_date)

# TODO get the institution
            votations = xml_sitting.xpath("./Votation")
            for xml_votation in votations:
                vot_num = xml_votation.get("idnum")
                om_votation = Votation.objects.get(idnum=vot_num,
                    sitting=om_sitting)

                if om_votation != None:
                    continue

                om_votation = Votation()
                om_votation.sitting = om_sitting
                om_votation.idnum = vot_num
                om_votation.act_descr = "" # TODO get it from the votation
                om_votation.charge_set = None # TODO get it from the votation
                om_votation.n_legal = xml_sitting.get("legal_number")
                om_votation.n_presents = xml_sitting.get("presents")
                om_votation.n_yes = xml_sitting.get("counter_yes")
                om_votation.n_no = xml_sitting.get("counter_no")
                om_votation.n_abst = xml_sitting.get("counter_abs")
# TODO majority not present in XML?
                om_votation.outcome = xml_sitting.get("outcome") # decode

                chargevotes = xml_votation.xpath("./ChargeVote")
                for xml_chargevote in chargevotes:
                    om_cv = ChargeVote()
                    om_cv.votation = om_votation
                    om_cv.vote = xml_chargevote.get("vote") # decode

                    charge_pk = xml_chargevote.get("cardID")
                    if charge_pk > 0:
                        om_charge = InstitutionCharge.objects.get(pk=charge_pk)
                        if om_charge == None:
# TODO create the InstitutionCharge with the information of the linked person
                            self.out.write("Unable to find InstitutionCharge (pk=%d)" % charge_pk)                    

                        om_cv.charge = om_charge          

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
                self.handleFile(filename=filename)
        except Exception as e:
            traceback.print_exc()
            raise CommandError("Error executing command: %s" % e)

