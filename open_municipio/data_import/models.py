from open_municipio.people.models import Person, InstitutionCharge, \
    CompanyCharge, AdministrationCharge
from django.db import models

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

import logging

class Provider(models.Model):
    desc = models.CharField(max_length=255)

    def __unicode__(self):
        return u"%s" % self.desc

class LookupObject(models.Model):
    local = None
    external = None
    provider = None

    class Meta:
        abstract = True

    @staticmethod
    def lookup(objects, external):
        return objects.get(external=external).local

    def __str__(self):
        return "%s [%s > %s]" % (self.local, self.provider, self.external)
    def __unicode__(self):
        return u"%s [%s > %s]" % (self.local, self.provider, self.external)

class LookupPerson(LookupObject):
    local = models.ForeignKey(Person)
    external = models.CharField(unique=True, max_length=256)
    provider = models.ForeignKey(Provider)

    @staticmethod
    def lookup(external):
        return LookupObject.lookup(LookupPerson.objects, external)

class LookupInstitutionCharge(LookupObject):
    local = models.ForeignKey(InstitutionCharge)
    external = models.CharField(unique=True, max_length=256)
    provider = models.ForeignKey(Provider)

    @staticmethod
    def lookup(external):
        return LookupObject.lookup(LookupInstitutionCharge.objects, 
            external)


class LookupCompanyCharge(LookupObject):
    local = models.ForeignKey(CompanyCharge)
    external = models.CharField(unique=True, max_length=256)
    provider = models.ForeignKey(Provider)

    @staticmethod
    def lookup(external):
        return LookupObject.lookup(LookupCompanyCharge.objects, external)

class LookupAdministrationCharge(LookupObject):
    local = models.ForeignKey(AdministrationCharge)
    external = models.CharField(unique=True, max_length=256)
    provider = models.ForeignKey(Provider)

    @staticmethod
    def lookup(external):
        return LookupAdministrationCharge.lookup(LookupAdministrationCharge.objects, external)

class PersonSeekerMixin:
    logger = logging.getLogger("import")
    
    def lookup_person(self, external):
        return LookupPerson.lookup(external)


class ChargeSeekerFromMapMixin:
    logger = logging.getLogger("import")

    def lookup_charge(self, external):
        self.logger.info("Try to detect institution (%s)..." % external)
        try:
            institutionLookup = LookupInstitutionCharge.lookup(external)
            return institutionLookup
        except Exception:
            pass

        self.logger.info("Try to detect company...")
        try:
            companyLookup = LookupCompanyCharge.lookup(external)
            return companyLookup
        except Exception:
            pass

        self.logger.info("Try to detect administration ...")
        try:
            administratorLookup = LookupAdministratorCharge.lookup(external)
            return administratorLookup
        except Exception:
            pass

class ChargeSeekerMixin:
    logger = logging.getLogger("import")

    def lookup_charge(self, person, institution, as_of=None):
        """
        lookup for the charge of the person at a specific moment in time. the
        person is an instance of class Person. institution is an instance of
        class Institution. as_of is a string of format "YYYY-MM-DD"
        """

        if person == None:
            raise Exception("Can't search a charge for no person")

        if institution is None:
            raise Exception("Can't search a charge without an institution")

        try:
            charge = person.get_current_charge_in_institution(institution, 
                moment=as_of)
            return charge
        except ObjectDoesNotExist:
            self.logger.warning("Can't find charge for person %s" % person)
            return None
        except MultipleObjectsReturned:
            self.logger.warning("Found more than one person or charge for id %s (institution %s) in OM. Skipping." % (person, institution))
            return None
