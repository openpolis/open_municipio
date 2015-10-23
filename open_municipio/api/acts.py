from rest_framework import viewsets
from open_municipio.acts.models import Deliberation, CGDeliberation, Motion, \
                        Decree, Decision, Interpellation, Interrogation, Speech
from open_municipio.api.serializers import DeliberationSerializer, \
                        CGDeliberationSerializer


class DeliberationViewSet(viewsets.ReadOnlyModelViewSet):
    
    queryset = Deliberation.objects.all()
    serializer_class = DeliberationSerializer


class CGDeliberationViewSet(viewsets.ReadOnlyModelViewSet):
    
    queryset = CGDeliberation.objects.all()
    serializer_class = CGDeliberationSerializer


