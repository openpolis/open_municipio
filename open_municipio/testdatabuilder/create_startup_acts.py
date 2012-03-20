#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import lipsum
import datetime
import open_municipio.testdatabuilder.random_items_factory as random_factory

from open_municipio.people.models import *
from open_municipio.acts.models import *

# cleanup
Act.objects.all().delete()

election_date = '2010-06-14'

g = lipsum.Generator()

#
# creazione proposte di delibera di consiglio
#
institution = Institution.objects.get(slug='consiglio-comunale')

for i in range(1, 5):
    d = Deliberation(
        idnum="%s" % i,
        title=g.generate_sentence(),
        text=g.generate_paragraph(),
        presentation_date=datetime.date.today() - datetime.timedelta(days=random.randint(1, 10)),
        emitting_institution=institution,
        initiative=Deliberation.COUNSELOR_INIT,
    )
    d.save()
    print "Delibera %s - %s creata" % (d.idnum, d.title)
    
    nf = random.randint(1, 3)
    nc = random.randint(0, 5)
    print "Aggiunta di %s primi firmatari"  % nf
    maj = random.choice([1, 1, 1, 1, 1, 1, 1, 1, 0]) # first-signers and co-signers come from maj 90% of the times
    presenters = random_factory.get_institution_charges(majority=maj, n=(nf+nc))
        
    for presenter in presenters[0:nf]:
        act_support = ActSupport(
            charge=presenter, act=d, 
            support_type=ActSupport.SUPPORT_TYPE.first_signer,
            support_date=d.presentation_date
        )
        print "%s" % presenter
        act_support.save()
    
    print "Aggiunta di %s co firmatari"  % nc
    for presenter in presenters[nf:]:
        act_support = ActSupport(
            charge=presenter, act=d, 
            support_type=ActSupport.SUPPORT_TYPE.co_signer,
            support_date=d.presentation_date
        )
        print "%s" % presenter
        act_support.save()
    
    na = random.randint(0, 5)
    print "Aggiunta di %s allegati" % na
    random_factory.generate_random_act_attach(d, n=na)

print "ok"
