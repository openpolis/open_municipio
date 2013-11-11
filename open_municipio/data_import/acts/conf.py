from open_municipio.people.models import CityCouncil as OMCityCouncil, \
    CityGovernment as OMCityGovernment, Mayor as OMMayor

from open_municipio.acts.models import CGDeliberation, Deliberation, Motion, Agenda, Amendment


# see the INITIATIVE_TYPES field in open_municipio.acts.models.Deliberation
OM_DELIBERATION_INITIATIVE_MAP = {
    "council_member" : 'COUNSELOR',
    "mayor" : 'MAYOR',
    "city_government" : 'GOVERNMENT',
}

OM_EMITTING_INSTITUTION_MAP = { 
    "CityGovernmentDeliberation" : OMCityGovernment().as_institution,
    "CouncilDeliberation" : OMCityCouncil().as_institution,
    "Motion" : OMCityCouncil().as_institution,
    "Agenda" : OMCityCouncil().as_institution,
    "Amendment" : OMCityCouncil().as_institution,
}

OM_ACT_MAP = {
    "CityGovernmentDeliberation" : CGDeliberation,
    "CouncilDeliberation" : Deliberation,
    "Motion" : Motion,
    "Agenda" : Agenda,
    "Amendment" : Amendment,
}