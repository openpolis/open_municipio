#!/usr/bin/env python
# -*- coding: utf8 -*-
from django.conf import settings

import open_municipio.testdatabuilder.random_items_factory as random_factory
from open_municipio.people.models import *
from open_municipio.votations.models import *

from datetime import *
import random
import itertools

# cleanup
Sitting.objects.all().delete()
Votation.objects.all().delete()

council_institution = Institution.objects.get(institution_type=Institution.COUNCIL)
# create council sitting
s1 = Sitting(
    idnum="1",
    number=1,
    date="2012-01-12",
    institution=council_institution
)
s1.save()
print "Seduta 1 creata"


# TODO:
# .. yes and no percentages vary according to group and majority


# generates 10 votations related to sitting s1
# 
for i in range(1, 10):
    
    # add a votation
    v = Votation(
        sitting=s1,
        idnum="%s" % i,
        n_legal=20,
    )
    v.save();
    print "Votazione %s creata"  % i
    
    # define vote weights
    # itertools.chain.from_iterable flattens a nested list of lists
    # [i]*N creates a list of N integers i
    # choosing randomly from the flattened lists is almost equivalent
    # to choosing with weighted probabilities
    vw = list(itertools.chain.from_iterable([
        [0]*30,  # 30% NO
        [1]*60,  # 60% YES
        [2]*5,   #  5% ABSTAINED
        [4]*5    #  5% ABSENT
    ])) 
    
    for charge in council_institution.institutioncharge_set.all():
        if (charge.charge_type == InstitutionCharge.COUNCIL_PRES_CHARGE or
            charge.charge_type == InstitutionCharge.COUNCIL_VICE_CHARGE):
            # president and vicepresident do not vote twice
            continue
        else:
            # votings are drawn randomly with weighted probabilities
            vote = random.choice(vw)
        
        charge_vote = ChargeVote.objects.create(votation=v, charge=charge, vote=vote)
        charge_vote.save()
        # print "%s voted %s" % (charge, charge_vote.vote)
    print "Voti creati"
    
    
    # compute voting totals
    v.n_yes = ChargeVote.objects.filter(votation=v, vote=ChargeVote.YES).count()
    v.n_no = ChargeVote.objects.filter(votation=v, vote=ChargeVote.NO).count()
    v.n_abst = ChargeVote.objects.filter(votation=v, vote=ChargeVote.ABSTAINED).count()
    n_president = ChargeVote.objects.filter(votation=v, vote=ChargeVote.PRES).count()
    v.n_present = v.n_yes + v.n_no + v.n_abst + n_president
    v.n_maj = int(v.n_present / 2) + 1
    if v.n_yes >= v.n_maj:
        v.outcome = Votation.PASSED
    else:
        v.outcome = Votation.REJECTED
    v.save()
    
    print "Totali"
    print "  Presenti: %s, Maggioranza: %s" % (v.n_present, v.n_maj)
    print "  %s YES, %s NO, %s ABSTAINED" % (v.n_yes, v.n_no, v.n_abst)
    print "  Voto %s" % (v.get_outcome_display())
