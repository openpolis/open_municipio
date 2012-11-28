from open_municipio.people.models import CityCouncil as OMCityCouncil


# see the INITIATIVE_TYPES field in open_municipio.acts.models.Deliberation
OM_DELIBERATION_INITIATIVE_MAP = {
    "council_member" : 'COUNSELOR',
}

OM_EMITTING_INSTITUTION_MAP = { 
    "CouncilDeliberation" : OMCityCouncil().as_institution,
    "Motion" : OMCityCouncil().as_institution,
    "Agenda" : OMCityCouncil().as_institution,
}
