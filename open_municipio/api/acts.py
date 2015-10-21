from tastypie.resources import ModelResource
from open_municipio.acts.models import Deliberation, CGDeliberation, Motion, \
                        Decree, Decision, Interpellation, Interrogation, Speech


class DeliberationResource(ModelResource):

    class Meta:
        queryset = Deliberation.objects.all()
        resource_name = "deliberation"


class CGDeliberationResource(ModelResource):

    class Meta:
        queryset = CGDeliberation.objects.all()
        resource_name = "cgdeliberation"


class MotionResource(ModelResource):

    class Meta:
        queryset = Motion.objects.all()
        resource_name = "deliberation"


class DecreeResource(ModelResource):

    class Meta:
        queryset = Decree.objects.all()
        resource_name = "decree"


class DecisionResource(ModelResource):

    class Meta:
        queryset = Decision.objects.all()
        resource_name = "decision"


class InterpellationResource(ModelResource):

    class Meta:
        queryset = Interpellation.objects.all()
        resource_name = "interpellation"


class InterrogationResource(ModelResource):

    class Meta:
        queryset = Interrogation.objects.all()
        resource_name = "interrogation"


class SpeechResource(ModelResource):

    class Meta:
        queryset = Speech.objects.all()
        resource_name = "speech"

