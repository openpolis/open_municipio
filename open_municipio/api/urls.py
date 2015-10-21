from django.conf.urls.defaults import *

from tastypie.api import Api

from open_municipio.api.people import PersonResource, InstitutionResource, \
        InstitutionChargeResource, AdministrationChargeResource, OfficeResource
from open_municipio.api.acts import DeliberationResource, CGDeliberationResource,\
        MotionResource, DecreeResource, DecisionResource, InterrogationResource,\
        InterpellationResource, SpeechResource



api = Api(api_name='v1')

# acts
api.register(DeliberationResource())
api.register(CGDeliberationResource())
api.register(MotionResource())
api.register(DecreeResource())
api.register(DecisionResource())
api.register(InterpellationResource())
api.register(InterrogationResource())
api.register(SpeechResource())

# people
api.register(PersonResource())
api.register(InstitutionResource())
api.register(InstitutionChargeResource())
api.register(OfficeResource())
api.register(AdministrationChargeResource())


urlpatterns = patterns('',
    url(r'^', include(api.urls)),
)
