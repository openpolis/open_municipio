#!/usr/bin/env python
# -*- coding: utf8 -*-
from datetime import *
from random import choice

import random_items_factory

from open_municipio.people.models import *
from django.conf import settings

# cleanup
Person.objects.all().delete()
InstitutionCharge.objects.all().delete()
Institution.objects.all().delete()
Group.objects.all().delete()

election_date = '2010-06-14'
n_consiglieri = 32
n_membri_commissione = 15
n_assessori = 7

#
# creazione istituzioni
#
print "Istituzioni"
sindaco_inst = Institution(
    name='Sindaco', institution_type=Institution.MAYOR, 
    description="Descrizione dell'istituzione ufficio del sindaco"
)
sindaco_inst.save()
print "  sindaco"

giunta_inst = Institution(
    name='Giunta comunale', institution_type=Institution.TOWN_GOVERNMENT, parent=sindaco_inst,
    description="Descrizione dell'istituzione Giunta"
)
giunta_inst.save()
print "  giunta"

consiglio_inst = Institution(
    name='Consiglio comunale', institution_type=Institution.COUNCIL, parent=sindaco_inst,
    description="Descrizione dell'istituzione Consiglio"
)
consiglio_inst.save()
print "  consiglio"

# commissioni
comm_descrizioni = [
    u"Affari Istituzionali, Personale e Partecipazione",
    u"Urbanistica, Infrastrutture e Lavori pubblici",
    u"Città sostenibile (Ambiente, Mobilità, Energia, Trasporto pubblico),frazioni, attività produttive, sport",
    u"Servizi alla Persona, Pubblica Istruzione e Politiche Giovanili",
    u"Cultura, Promozione e Turismo",
    u"Risorse Finanziarie e Patrimonio"
]
commissioni = []
print "  commissioni"
for c in range(0,len(comm_descrizioni)):
    print "    %s - %s" % (c, comm_descrizioni[c])
    comm_inst = Institution(
        name='%d^ commissione' % (c+1), institution_type=Institution.COMMITTEE, parent=consiglio_inst,
        description=comm_descrizioni[c]
    )
    comm_inst.save()
    commissioni.append(comm_inst)


# gruppi consiliari
gruppi = [
    { 'name': u"Partito democratico", 'acronym': 'PD', 'is_maj': False, 'perc': 28 },
    { 'name': u"Popolo delle Libertà", 'acronym': 'PDL', 'is_maj': True, 'perc': 33 },
    { 'name': u"Il bene comune", 'acronym': 'IBC', 'is_maj': False, 'perc': 7  },
    { 'name': u"Lista futura", 'acronym': 'LF', 'is_maj': True, 'perc': 15 },
    { 'name': u"Raggruppamento civico", 'acronym': 'RCIV', 'is_maj': True, 'perc': 4 },
    { 'name': u"Nostalgia dei bei tempi", 'acronym': 'NBT', 'is_maj': False, 'perc': 5 },
    { 'name': u"Gruppo misto", 'acronym': 'GM', 'is_maj': None, 'perc': 8 }
]    

# creazione gruppi
print "Gruppi"
for g in gruppi:
    gruppo = Group(name=g['name'], acronym=g['acronym'])
    gruppo.save()
    is_maj = GroupIsMajority(start_date=election_date, is_majority=g['is_maj'], group=gruppo)
    is_maj.save()
    g['obj'] = gruppo
    print "  %s" % gruppo

#
# creazione incarichi (e persone)
#


print "Incarichi"

print "  sindaco"
sindaco_pers = random_items_factory.create_person()
print sindaco_pers
sindaco_charge = InstitutionCharge(
    description="Descrizione incarico di sindaco",
    start_date = election_date,
    person = sindaco_pers,
    institution = sindaco_inst,
    charge_type = InstitutionCharge.MAYOR_CHARGE
)
sindaco_charge.save()

# creazione consiglieri
print "  consiglieri"
consiglieri = []
pres_created = False
vice_created = False
for i in range(0, n_consiglieri):
    pers = random_items_factory.create_person()
    charge = InstitutionCharge(
        description="Consigliere semplice",
        start_date = election_date,
        person = pers,
        institution = consiglio_inst,
        charge_type = InstitutionCharge.COUNSELOR_CHARGE
        )
    charge.save()
    consiglieri.append(charge)
    
    # assegnazione gruppo casuale (in base alle perc)
    cnt = 0
    while True:
        group = choice(gruppi)
        if 'remaining_perc' not in group:
            group['remaining_perc'] = group['perc']
        group['remaining_perc'] -= 100.0/n_consiglieri
        cnt += 1
        if group['remaining_perc'] > 0 or cnt > 10:
            break
    
    # presidente
    if not pres_created and group['acronym'] == 'PDL':
        pres_charge = InstitutionCharge(
            description="Presidente del Consiglio Comunale",
            start_date = election_date,
            person = pers,
            institution = consiglio_inst,
            charge_type = InstitutionCharge.COUNCIL_PRES_CHARGE
        )
        pres_charge.save()
        pres_created = True
    
    # vice presidente
    if not vice_created and group['acronym'] == 'PD':
        vice_charge = InstitutionCharge(
            description="Vicepresidente del Consiglio Comunale",
            start_date = election_date,
            person = pers,
            institution = consiglio_inst,
            charge_type = InstitutionCharge.COUNCIL_VICE_CHARGE
        )
        vice_charge.save()
        vice_created = True
        
    gc = GroupCharge.objects.create(group=group['obj'], charge=charge, start_date=election_date)
    if group['obj'].counselor_set.count == 0:
        gc.charge_description = "Capogruppo"
    gc.save()
    print "    %s - %s (%s)" % (i, pers, group['acronym'])



# creazione giunta
print "  giunta"
assessorati = [
     "Città Sostenibile (Ambiente, Mobilità, Trasporto Pubblico), Sport, Politiche Giovanili, Frazioni",
     "Urbanistica",
     "Attività Economiche, Pari Opportunità, Partecipazione",
     "Lavori Pubblici",
     "Risorse Finanziarie e Patrimoniali",
     "Cultura e Pubblica Istruzione",
     "Servizi alla Persona, Sanità, Politiche per l’Integrazione ed Edilizia Residenziale Pubblica"
]
for i in range(0, len(assessorati)):
    pers = random_items_factory.create_person()
    charge = InstitutionCharge(
        description=assessorati[i],
        start_date = election_date,
        person = pers,
        institution = giunta_inst,
        charge_type = InstitutionCharge.ASSESSOR_CHARGE
        )
    charge.save()
    print "    %s - %s (%s)" % (i, pers, assessorati[i])
    
    
# assegnazione posti in commissioni (pesata con percentuali per gruppi)
print "  commissioni"
for c_inst in commissioni:
    print "    %s" % c_inst.name
    for g in gruppi:
        n_choices = int(g['perc'] * n_membri_commissione / 100)
        print "      %s (%s)" % (g['obj'].name, n_choices)
        if n_choices > 0.:
            gc_list = list(g['obj'].groupcharge_set.all())
            for i in range(0, n_choices):
                gc = choice(gc_list)
                gc_list.remove(gc)
                pers = gc.charge.person
                charge = InstitutionCharge(
                    description="Membro della commissione",
                    start_date = election_date,
                    person = pers,
                    institution = c_inst,
                    charge_type = InstitutionCharge.COMMITTEE_MEMBER_CHARGE
                    )
                charge.save()
                print "        %s - %s" % (i, pers)
            