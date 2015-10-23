from rest_framework import viewsets

from open_municipio.people.models import Person, Institution, InstitutionCharge, \
                                AdministrationCharge, Office

from open_municipio.api.serializers import PersonSerializer


class PersonViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Person.objects.all()
    serializer_class = PersonSerializer
