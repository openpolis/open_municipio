#!/usr/bin/env python
# -*- coding: utf8 -*-
try:
    import json
except ImportError:
    import simplejson as json
from om.api.clients import OmAPI
from piston_mini_client.auth import BasicAuthorizer
from random import choice
from datetime import *
from django.conf import settings


def unify(seq, idfun=None):  
  '''
  remove double elements from the seq list
  idfun is a callback to the identity function
  '''
  # order preserving 
  if idfun is None: 
    def idfun(x): return x 
  seen = {} 
  result = [] 
  for item in seq: 
    marker = idfun(item) 
    # in old Python versions: 
    # if seen.has_key(marker) 
    # but in new ones: 
    if marker in seen: continue 
    seen[marker] = 1 
    result.append(item) 
  return result


def create_person():
  '''
  create a random person in the db and return the person just created
  '''
  auth_api = OmAPI(service_root='http://localhost:8000/api/1.0',
                   auth=BasicAuthorizer(settings.API_USER, settings.API_PASSWORD))

  try:
    f = open("om/fixtures/op_politician_first_names_sex.csv", "r")
    l = open("om/fixtures/op_politician_last_names.csv", "r")
    loc = open("om/fixtures/op_politician_birth_locations.csv", "r")
    dat = open("om/fixtures/op_politician_birth_dates.csv", "r")

    first_names = unify(f.readlines())
    last_names = unify(l.readlines())
    birth_dates = unify(dat.readlines())
    birth_locations = unify(loc.readlines())
  
    first_name = choice(first_names)
    first_names.remove(first_name)
    first_name = first_name.strip()
    (names, sex) = first_name.split(',')
    names = names.split()
    first_name = choice(names)

    last_name = choice(last_names)
    last_names.remove(last_name)
    last_name = last_name.strip()

    birth_date = choice(birth_dates)
    birth_dates.remove(birth_date)
    birth_date = birth_date.strip()
    birth_date = datetime.strptime(birth_date, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
  
    birth_location = choice(birth_locations)
    birth_locations.remove(birth_location)
    birth_location = birth_location.strip()

    p_obj = {
      'first_name': first_name, 
      'last_name': last_name, 
      'birth_date': birth_date, 
      'birth_location': birth_location, 
      'sex': sex.lower()
    }
    
    # if the person exists, then return it, else create it and return it
    # avoid duplications
    p = json.loads(auth_api.get_persons_from_data(p_obj))
    if (len(p) == 0):
      auth_api.add_person(json.dumps(p_obj))
      p = json.loads(auth_api.get_persons_from_data(p_obj))

    return p[0]

      
  except IOError:
    print "Error while opening file"
    return 0
