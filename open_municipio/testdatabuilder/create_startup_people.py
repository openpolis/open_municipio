#!/usr/bin/env python
# -*- coding: utf-8 -*-
from random import choice
import open_municipio.testdatabuilder.random_items_factory as random_factory
from open_municipio.people.models import *

# cleanup
Person.objects.all().delete()
InstitutionCharge.objects.all().delete()
Institution.objects.all().delete()
Group.objects.all().delete()

election_date = '2008-05-08'
n_consiglieri = 40
n_membri_commissione = 15
n_assessori = 10

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
    name='Giunta comunale', institution_type=Institution.CITY_GOVERNMENT, parent=sindaco_inst,
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
    u"Bilancio e programmazione",
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
sindaco_pers = random_factory.create_person()
print sindaco_pers
sindaco_charge = InstitutionCharge(
    description="Descrizione incarico di sindaco",
    start_date = election_date,
    person = sindaco_pers,
    institution = sindaco_inst
)
sindaco_charge.save()

# creazione consiglieri
print "  consiglieri"
consiglieri = []
pres_created = False
vice_created = False
for i in range(0, n_consiglieri):
    pers = random_factory.create_person()
    charge = InstitutionCharge(
        start_date = election_date,
        person = pers,
        institution = consiglio_inst
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

    group['n_members'] = group['obj'].charge_set.count()

    # council president (second member of PDL group)
    if not pres_created and \
       group['acronym'] == 'PDL' and group['n_members'] == 1:
        pres_resp = InstitutionResponsability(
            description="Presidente del Consiglio Comunale",
            start_date=election_date,
            charge=charge,
            charge_type=InstitutionResponsability.CHARGE_TYPES.president
        )
        pres_resp.save()
        pres_created = True
        print "Council president created"

    # council vice president (second member of PD group)
    if not vice_created and \
       group['acronym'] == 'PD' and group['n_members'] == 1:
        vice_resp = InstitutionResponsability(
            description="Vicepresidente del Consiglio Comunale",
            start_date=election_date,
            charge=charge,
            charge_type=InstitutionResponsability.CHARGE_TYPES.vice
        )
        vice_resp.save()
        vice_created = True
        print "Council vice president created"

    gc = GroupCharge.objects.create(group=group['obj'], charge=charge, start_date=election_date)
    gc.save()

    # group leader creation (first member of each group)
    print "%s: " % group['n_members']
    if group['n_members'] == 0:
        group_resp = GroupResponsability(
            description="Capogruppo",
            start_date=election_date,
            charge=gc,
            charge_type=GroupResponsability.CHARGE_TYPES.leader
        )
        group_resp.save()
        print "Group leader created"

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
    pers = random_factory.create_person()
    charge = InstitutionCharge(
        description=assessorati[i],
        start_date = election_date,
        person = pers,
        institution = giunta_inst,
    )
    charge.save()
    print "    %s - %s (%s)" % (i, pers, assessorati[i])
    
    
# assegnazione posti in commissioni (pesata con percentuali per gruppi)
print "  commissioni"
for c_inst in commissioni:
    pres_created = False
    vice_created = False
    g_pres = choice(gruppi)
    g_vice = choice(gruppi)
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
                )
                charge.original_charge = pers.current_institution_charges[0]
                charge.save()
                print "        %s - %s" % (i, pers)

                # commission president (first choice)
                if g == g_pres and not pres_created:
                    pres_resp = InstitutionResponsability(
                        description="Presidente",
                        start_date=election_date,
                        charge=charge,
                        charge_type=InstitutionResponsability.CHARGE_TYPES.president
                    )
                    pres_resp.save()
                    pres_created = True
                    print "Commission president created"

                # commission vice president (first choice after president)
                if g==g_vice and not vice_created:
                    vice_resp = InstitutionResponsability(
                        description="Vicepresidente",
                        start_date=election_date,
                        charge=charge,
                        charge_type=InstitutionResponsability.CHARGE_TYPES.vice
                    )
                    vice_resp.save()
                    vice_created = True
                    print "Commission vice president created"


