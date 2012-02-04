#!/usr/bin/env python
# -*- coding: utf8 -*-
try:
    import json
except ImportError:
    import simplejson as json
from random import choice
from random import random

from datetime import *
from open_municipio.om.models import Person
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
  if the person already exists, return it
  '''
  try:
    f = open("open_municipio/om/fixtures/op_politician_first_names_sex.csv", "r")
    l = open("open_municipio/om/fixtures/op_politician_last_names.csv", "r")
    loc = open("open_municipio/om/fixtures/op_politician_birth_locations.csv", "r")
    dat = open("open_municipio/om/fixtures/op_politician_birth_dates.csv", "r")

    first_names = unify(f.readlines())
    last_names = unify(l.readlines())
    birth_dates = unify(dat.readlines())
    birth_locations = unify(loc.readlines())
  
    first_name = choice(first_names)
    first_names.remove(first_name)
    first_name = first_name.strip()
    (names, sex) = first_name.split(',')
    if sex == 'M':
        sex = Person.MALE_SEX
    else:
        sex = Person.FEMALE_SEX
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

    persons = Person.objects.filter(first_name=first_name, last_name=last_name, birth_date=birth_date, birth_location=birth_location)
    if (not persons):
        p = Person(first_name=first_name, last_name=last_name, birth_date=birth_date, birth_location=birth_location, sex=sex)
        p.save()
    else: 
        p = persons[0]

    return p

      
  except IOError:
    print "Error while opening file"
    return 0

def weighted_choice(weights):
    choice = random() * sum(weights)
    for i, w in enumerate(weights):
        choice -= w
        if choice < 0:
            return i
            

