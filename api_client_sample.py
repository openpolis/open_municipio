#!/usr/bin/env python
# -*- coding: utf8 -*-
try:
    import json
except ImportError:
    import simplejson as json
from om.api.clients import OmAPI
from piston_mini_client.auth import BasicAuthorizer
from create_random_persons import create_person
from django.conf import settings

'''
api = OmAPI(service_root='http://localhost:8000/api/1.0')

print "listing all persons"
persons = api.get_persons()
print persons
'''

auth_api = OmAPI(service_root='http://localhost:8000/api/1.0',
                 auth=BasicAuthorizer(settings.API_USER, settings.API_PASSWORD))
print "----"

p_obj = {
  'first_name': 'Guglielmo',
  'last_name': 'pok pf ok', 
  'birth_date': '1955-04-25', 
  'birth_location': 'Roma', 
  'sex': 'm'
}
p = create_person()
print "added a random person"
print p

'''
print "----"
print "retrieving a person"
p = auth_api.retrieve_person(person_id=p['id'])
print p

print "----"
print "removing a person"
auth_api.delete_person(id=p['id'])
'''
