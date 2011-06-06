#!/usr/bin/env python
# -*- coding: utf8 -*-
try:
    import json
except ImportError:
    import simplejson as json
import yaml
from om.api.clients import OmAPI
from piston_mini_client.auth import BasicAuthorizer
from datetime import *
from create_random_persons import create_person
from django.conf import settings

auth_api = OmAPI(service_root='http://localhost:8000/api/1.0',
                 auth=BasicAuthorizer(settings.API_USER, settings.API_PASSWORD))

'''
# working sample
i_obj = {'charges': [{'charge_type': 'may', 'person': '1', 'start_date': '2010-05-15'}], 'description': 'The Mayor institution not the charge', 'name': 'Mayor', 'institution_type': 'may'}
i = json.dumps(i_obj)
print "adding %s" % i
auth_api.add_institution(i)

'''

institution_file = open("om/fixtures/institutions.yaml", "r")
institutions = yaml.load(institution_file)

# first loop: add random persons
for i in sorted(institutions.iterkeys()):
  institution = institutions[i]
  charges = institution['charges']
  for c in sorted(charges.iterkeys()):
    charge = charges[c]
    if not 'person_ref' in charge:
      p = create_person()
      charge['person'] = p['id']
      

# second loop: create json-serializable python object from yaml-deserialized object  
# add references to persons created in the first loop
for i in sorted(institutions.iterkeys()):
  institution = institutions[i]
  i_obj = {'name': institution['name'], 'institution_type': institution['institution_type'], 'description': ''}
  if 'description' in institution:
    i_obj['description'] = institution['description']

  charges = institution['charges']
  i_obj['charges']= []
  for c in sorted(charges.iterkeys()):
    charge = charges[c]

    if 'person_ref' in charge:
      ref = charge['person_ref']
      charge['person'] = institutions['b_town_gov']['charges'][ref]['person']
      
    c_obj = {'charge_type': charge['charge_type'], 'start_date': charge['start_date'].strftime("%Y-%m-%d"), 'person': '%d' % charge['person']}

    i_obj['charges'].append(c_obj)

  print "adding %s" % i_obj
  auth_api.add_institution(json.dumps(i_obj))
