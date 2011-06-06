from piston.handler import AnonymousBaseHandler, BaseHandler
from piston.utils import rc, throttle, validate
from om.models import Person, Institution, InstitutionCharge
import logging

from django import forms

class InstitutionForm(forms.ModelForm):
   class Meta:
      model = Institution


class AnonymousInstitutionHandler(AnonymousBaseHandler):
  model = Institution
  fields = ('id', 'name', 'description', 'institution_type', 'parent')
  allowed_methods = ('GET')

class InstitutionHandler(BaseHandler):
  allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
  fields = ('id', 'name', 'description', 'institution_type', 'parent')
  exclude = ('id')
  model = Institution
  anonymous = AnonymousInstitutionHandler
    
  def read(self, request, id=None):
    base = self.model.objects
    
    if id:
      return base.get(pk=id)
    else:
      return base.all() # Or base.filter(...)

  def create(self, request):
    if request.content_type and request.data:
      data = request.data

      institution = self.model(
        name=data['name'],
        institution_type=data['institution_type']
      )
      if 'description' in data:
        institution.description = data['description']
      if 'parent' in data:
        institution.parent = data['parent']
        
      institution.save()

      for charge in data['charges']:
        InstitutionCharge(
          institution=institution, 
          person=Person.objects.get(pk=charge['person']),
          charge_type=charge['charge_type'],
          start_date=charge['start_date']).save()

      return rc.CREATED
    else:
      super(PersonHandler, self).create(request)


class PersonHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    fields = ('id', 'first_name', 'last_name', 'sex', 'birth_date', 'birth_location')
    exclude = ('id')
    model = Person
    anonymous = 'AnonymousPersonHandler'

    def read(self, request, id=None, first_name=None, last_name=None, birth_date=None, birth_location=None):
      base = self.model.objects

      if id:
        return base.get(pk=id)
      else:
        q = base.all()
        if last_name:
          q = q.filter(last_name__iexact=last_name)
        if first_name:
          q = q.filter(first_name__iexact=first_name)
        if birth_date:
          q = q.filter(birth_date__iexact=birth_date)
        if birth_location:
          q = q.filter(birth_location__iexact=birth_location)
        return q 

class AnonymousPersonHandler(AnonymousBaseHandler, PersonHandler):
   model = Person
   fields = ('id', 'first_name', 'last_name', 'sex', 'birth_date', 'birth_location')
   allowed_methods = ('GET')



class ArbitraryDataHandler(BaseHandler):
    methods_allowed = ('GET',)

    def read(self, request, username, data):
      user = User.objects.get(username=username)

      return { 'user': user, 'data_length': len(data) }