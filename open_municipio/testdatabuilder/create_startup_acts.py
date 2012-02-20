#!/usr/bin/env python
# -*- coding: utf8 -*-
import random
import datetime
import lipsum

import open_municipio.testdatabuilder.random_items_factory as random_factory

from open_municipio.people.models import *
from open_municipio.acts.models import *
from django.conf import settings

# cleanup
Act.objects.all().delete()

election_date = '2010-06-14'

g = lipsum.Generator()


#
# creazione proposta di delibera di consiglio
#
institution = Institution.objects.get(slug='consiglio-comunale')


d1 = Deliberation(
    idnum="a1",
    title=g.generate_sentence(),
    text=g.generate_paragraph(),
    presentation_date=datetime.date.today() - datetime.timedelta(days=random.randint(1, 10)),
    emitting_institution=institution,
    initiative=Deliberation.COUNSELOR_INIT,
)
d1.save()
print "Delibera %s - %s creata" % (d1.idnum, d1.title)

print "Aggiunta di 3 firmatari"
for presenter in random_factory.get_institution_charges(institution='consiglio', majority=True, n=3):
    act_support = ActSupport(
        charge=presenter, act=d1, 
        support_type=ActSupport.FIRST_SIGNER,
        support_date=d1.presentation_date
    )
    print "%s" % (presenter)
    act_support.save()
    
print "Aggiunta di N allegati (random tra 0 e 5)"
random_factory.generate_random_act_attach(d1, n=random.randint(0, 5))

print "ok"
