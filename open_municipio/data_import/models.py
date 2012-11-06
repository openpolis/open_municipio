from open_municipio.people.models import Person, InstitutionCharge, \
    CompanyCharge, AdministrationCharge
from django.db import models

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

import logging

# TODO add a field to select the provider
class LookupObject(models.Model):
    local = None
    provider = None

    class Meta:
        abstract = True

    @staticmethod
    def lookup(objects, provider):
        return objects.get(provider=provider).local

    def __str__(self):
        return "%s [%s]" % (self.local,self.provider)
    def __unicode__(self):
        return u"%s [%s]" % (self.local, self.provider)

class LookupPerson(LookupObject):
    local = models.ForeignKey(Person)
    provider = models.CharField(unique=True, max_length=256)

    @staticmethod
    def lookup(provider):
        return LookupObject.lookup(LookupPerson.objects, provider)

class LookupInstitutionCharge(LookupObject):
    local = models.ForeignKey(InstitutionCharge)
    provider = models.CharField(unique=True, max_length=256)

    @staticmethod
    def lookup(provider):
        return LookupObject.lookup(LookupInstitutionCharge.objects, 
            provider)


class LookupCompanyCharge(LookupObject):
    local = models.ForeignKey(CompanyCharge)
    provider = models.CharField(unique=True, max_length=256)

    @staticmethod
    def lookup(provider):
        return LookupObject.lookup(LookupCompanyCharge.objects, provider)

class LookupAdministrationCharge(LookupObject):
    local = models.ForeignKey(AdministrationCharge)
    provider = models.CharField(unique=True, max_length=256)

    @staticmethod
    def lookup(provider):
        return LookupAdministrationCharge.lookup(LookupAdministrationCharge.objects, provider)

class PersonSeekerMixin:
    logger = logging.getLogger("import")
    
    def lookup_person(self, provider):
        return LookupPerson.lookup(provider)


class ChargeSeekerFromMapMixin:
    logger = logging.getLogger("import")

    def lookup_charge(self, provider):
        self.logger.info("Try to detect institution (%s)..." % provider)
        try:
            institutionLookup = LookupInstitutionCharge.lookup(provider)
            return institutionLookup
        except Exception:
            pass

        self.logger.info("Try to detect company...")
        try:
            companyLookup = LookupCompanyCharge.lookup(provider)
            return companyLookup
        except Exception:
            pass

        self.logger.info("Try to detect administration ...")
        try:
            administratorLookup = LookupAdministratorCharge.lookup(provider)
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
