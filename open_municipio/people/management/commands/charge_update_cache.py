'''
Created on 14/set/2013

@author: spegni
'''
import datetime
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from open_municipio.votations.models import Votation
from open_municipio.people.models import municipality

class Command(BaseCommand):
    
    def handle(self, *args, **options):

        president = municipality.council.president
        print("Update city council president: %s" % president.charge)
        president.charge.update_presence_cache()
        president.charge.update_rebellion_cache()

        vps = municipality.council.vicepresidents
        for curr in vps:
            print("Update city council vice presidents: %s" % curr.charge)
            curr.charge.update_presence_cache()
            curr.charge.update_rebellion_cache()

        for charge in municipality.council.members:
            print("Update charge: %s" % charge)
            charge.update_presence_cache()
            charge.update_rebellion_cache()
            
