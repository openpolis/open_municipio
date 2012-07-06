from django.core.management.base import BaseCommand, CommandError

from lxml import etree
from os import path

from open_municipio.people.models import InstitutionCharge, Person, CityCouncil

import traceback
from open_municipio.settings_import import XML_TO_OM_INST, IMPORT_NS, BIRTH_DATE_DEF, GENDER_DEF, START_DATE_DEF

class Command(BaseCommand):
    args = "<filename filename ...>"
    help = "Import the charges contained in the specified XML documents"

    def revLookup(self, choicelist, value):
        for (key,currvalue) in choicelist:
            if currvalue == value:
                return key
        return None

    def handlePerson(self, xml_person):
        first_name = xml_person.get("first_name")
        last_name = xml_person.get("last_name")
        try:
            om_person = Person.objects.all().get(first_name=first_name,
                last_name=last_name)
            print("Person %s %s already imported" % (first_name,last_name))
            return om_person
        except Exception:
            # do nothing, continue to import it
            om_person = None

        om_person = Person()
        om_person.first_name = first_name
        om_person.last_name = last_name
        om_person.birth_date = BIRTH_DATE_DEF
        om_person.gender = GENDER_DEF
        om_person.save()
        return om_person
    
    def lookupCharge(self, om_person, om_institution):
        try:
            om_charge = InstitutionCharge.objects.all().get(person=om_person, institution=om_institution)
        except Exception:
            om_charge = None

        return om_charge
        

    def handleCharge(self, xml_charge, om_institution):
        charge_id = xml_charge.get("id")
        try:
            om_charge = InstitutionCharge.objects.all().get(pk=charge_id)
            print("Charge (pk=%d) already imported" % charge_id)
            return
        except Exception:
            # not found, continue with importing
            om_charge = None

        persons = xml_charge.xpath("./om:Person", namespaces=IMPORT_NS)
        if len(persons) > 1:
            print("Alert! More than one Person found for this Charge")
        elif len(persons) == 1:
            print("Found Person data in XML document")
        else:
            print("No Person data found")

        for xml_person in persons:
            om_person = self.handlePerson(xml_person)

            charge_desc = xml_charge.get("description")
            charge_type = self.revLookup(InstitutionCharge.CHARGE_TYPES, charge_desc)
            if charge_type == None:
                print("Unable to find charge_type for '%s'. Interrupt import current Charge" % charge_desc)
                continue

            om_charge = self.lookupCharge(om_person, om_institution)

            if om_charge != None:
                print("Charge already present (%s %s at %s), no need to import" % 
                    (om_person.first_name, om_person.last_name, om_institution.name))
                continue

            charge_pk = xml_charge.get("id")
            om_charge = InstitutionCharge()
            om_charge.pk = int(charge_pk)
            om_charge.person = om_person
            om_charge.institution = om_institution
            om_charge.start_date = START_DATE_DEF
            om_charge.charge_type = charge_type
            om_charge.save()
            print("Imported Charge (%s %s at %s) successfully (pk=%d)" % 
                    (om_person.first_name, om_person.last_name, om_institution.name,
                    om_charge.pk, charge_pk))


    def handleCouncil(self, xml_council):
        charges = xml_council.xpath("./om:Charge", namespaces=IMPORT_NS)
        om_institution = CityCouncil().as_institution
        print("Found %d Charges to import" % len(charges))
        for xml_charge in charges:
            self.handleCharge(xml_charge, om_institution)

    def handleFile(self, filename):
        if not path.isfile(filename):
            raise IOError("File %s does not exist" % filename)

        tree = etree.parse(filename)

        councils = tree.xpath("/om:People/om:Institutions/om:Council", 
            namespaces=IMPORT_NS);

        if len(councils) > 1:
            print("More than one element Council found, this should not happen")
        elif len(councils) == 1:
            print("Found Council element to import")       
        for xml_council in councils:
            self.handleCouncil(xml_council)

    def print_help(self):
        self.stdout.write("Command syntax:\n")
        self.stdout.write("importcharges %s\n" % self.args)
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

