from tastypie.resources import ModelResource
from tastypie import fields

from open_municipio.people.models import Person, Institution, InstitutionCharge, \
                                AdministrationCharge, Office


class PersonResource(ModelResource):

    class Meta:
        queryset = Person.objects.all()
        resource_name = "person"


class InstitutionResource(ModelResource):
 
    parent = fields.ForeignKey('InstitutionResource', 'parent', null=True)
    
    
    class Meta:
        queryset = Institution.objects.all()
        resource_name = "institution"
    
        fields = [ 'parent', 'institution_type', 'name', 'description', 'slug', ]


class InstitutionChargeResource(ModelResource):

    person = fields.ForeignKey(PersonResource, 'person')
    institution = fields.ForeignKey(InstitutionResource, 'institution')
 
    class Meta:

        queryset = InstitutionCharge.objects.all()
        resource_name = "institutioncharge"


class OfficeResource(ModelResource):

    class Meta:
        queryset = Office.objects.all()
        resource_name = "office"


class AdministrationChargeResource(ModelResource):
 
    person = fields.ForeignKey(PersonResource, 'person')
    office = fields.ForeignKey(OfficeResource, 'office')
  
    class Meta:
        queryset = AdministrationCharge.objects.all()
        resource_name = "administrationcharge"
