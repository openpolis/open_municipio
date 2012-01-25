from piston_mini_client import PistonAPI
from piston_mini_client.validators import validate, validate_pattern, basic_protected
from piston_mini_client.failhandlers import NoneFailHandler
import urllib

class OmAPI(PistonAPI):
  '''
  This class is a wrapper to the RESTful API provided by django-piston
  on the django models of the om application.
  
  Use this class in your internal python scripts, to interface external parsers 
  and complete other management tasks.
  '''
  # the default root of the service URI, in case it was not specified in the script
  default_service_root = 'http://localhost:8000/api/1.0'

  @validate_pattern('person_id', r'\d+', required=False)
  def get_persons(self, person_id=None):
    '''
    get all Persons, or a single one if an id is specified
    if specified, the ID must be made out of digits (\d+ regexp)
    '''
    if person_id is None:
      return self._get('persons')
    else:
      return self._get('persons/%s/' % (person_id, ))

  @validate_pattern('person_id', r'\d+')
  def retrieve_person(self, person_id):
    '''
    just get a single Person
    the ID must be made out of digits and it is needed
    '''
    return self._get('persons/%s/' % (person_id, ))


  def get_persons_from_data(self, data_dict):
    '''
    get all Persons veryfing exactly data
    data must be a dictionary, it can contain first_name, last_name, birth_date, birth_location
    in one of these combinations:
     - last_name
     - first_name + last_name
     - first_name + last_name + birth_date
     - first_name + last_name + birth_date + birth_location
    more than one json ``records`` can be returned
    '''
    data_qs = u''
    if 'last_name' in data_dict:
      data_qs = data_dict['last_name']
    if 'first_name' in data_dict and 'last_name' in data_dict:
      data_qs = "%s/%s" % (data_dict['first_name'], data_dict['last_name'])
      if 'birth_date' in data_dict:
        data_qs += "/%s" % (data_dict['birth_date'],)
        if 'birth_location' in data_dict:
          data_qs += "/%s" % (data_dict['birth_location'],)

    return self._get('persons_lookup/%s/' % (urllib.quote(data_qs), ))


  @basic_protected()
  def add_person(self, person_data):
    """add a Person
    data must be passed as a python object
    """
    return self._post('persons/', person_data)
    
  @basic_protected()
  @validate_pattern('id', r'\d+')
  def delete_person(self, id):
    '''
    delete a single Person
    the ID must be made out of digits and it is needed
    '''
    return self._delete('persons/%s/' % (id, ))


  @basic_protected()
  def add_institution(self, data):
    """add an Institution
    data must be passed as a python object
    """
    return self._post('institutions/', data)

  @basic_protected()
  @validate_pattern('id', r'\d+')
  def delete_institution(self, id):
    '''
    delete a single Institution
    the ID must be made out of digits and it is needed
    '''
    return self._delete('institutions/%s/' % (id, ))
    
