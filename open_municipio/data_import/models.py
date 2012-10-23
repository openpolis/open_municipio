from open_municipio.people.models import Person
from django.db import models

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

import logging

# TODO add a field to select the provider
class LookupPerson(models.Model):
    local = models.ForeignKey(Person)
    provider = models.CharField(unique=True, max_length=256)

    def __str__(self):
        return "%s [%s]" % (self.local,self.provider)
    def __unicode__(self):
        return u"%s [%s]" % (self.local, self.provider)

class PersonSeekerMixin:
    logger = logging.getLogger("import")
    
    def lookup_person(self, provider):
        return LookupPerson.objects.get(provider=provider).local

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
