from django.conf.urls import patterns, url
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
from om.api.handlers import PersonHandler, InstitutionHandler

auth = HttpBasicAuthentication(realm="openmunicipio API")
ad = { 'authentication': auth }


person_resource = Resource(handler=PersonHandler, **ad)
institution_resource = Resource(handler=InstitutionHandler, **ad)

urlpatterns = patterns('',
    url(r'^persons/$', person_resource),
    url(r'^persons/(?P<id>\d+)/$', person_resource), 
    url(r'^persons_lookup/(?P<last_name>[^/]*)/$', person_resource), 
    url(r'^persons_lookup/(?P<first_name>[^/]*)/(?P<last_name>[^/]*)/$', person_resource), 
    url(r'^persons_lookup/(?P<first_name>[^/]*?)/(?P<last_name>[^/]*?)/(?P<birth_date>[-\d]*)/$', person_resource), 
    url(r'^persons_lookup/(?P<first_name>[^/]*?)/(?P<last_name>[^/]*?)/(?P<birth_date>[-\d]*?)/(?P<birth_location>.*)/$', person_resource), 
    url(r'^institutions/$', institution_resource),
    url(r'^institutions/(?P<id>\d+)/$', institution_resource), 
)
