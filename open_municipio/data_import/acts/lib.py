from django.utils import simplejson as json

from open_municipio.data_import.lib import DataSource, BaseReader, BaseWriter, JSONWriter, XMLWriter, OMWriter
# import OM-XML language tags
from open_municipio.data_import.om_xml import *

from lxml import etree

class ActsDataSource(DataSource):
    """
    A data source containing acts-related data.
    """
    pass

class BaseActsReader(BaseReader):
    """
    An abstract reader class parsing acts-relate//d data.
    
    This class encapsulates generic -- but acts-specific -- parsing logic. 
    It's intended to be subclassed (and its methods overriden) in order to adapt to 
    concrete scenarios. 
    """
    def read(self):
        # initialize the reader
        self.setup()
        # get the data source to read from
        data_source = self.get_data_source()
        # initialize the data source
        data_source.setup()
        
        self.acts = []
        
        # TODO extract the relevant information
        
        return self.acts;      


class BaseActsWriter(BaseWriter):
    """
    An abstract writer class that serializes internal representations 
    of acts-related data.
    
    This class encapsulates acts-specific serialization logic which is independent 
    from a specific output format. 
    """
    pass

class OMActsWriter(BaseActsWriter, OMWriter):
    """
    A writer class which outputs acts data as objects in the OpenMunicio model.
    """                        
    def write(self):
        raise NotImplementedError
    
# python object layer for imported data

# document section

class Act:
    id = ""
    content = ""
    file = None
    subscribers = [] # list of Charges
    
    def add_subscriber(self, charge):
        self.subscribers.append(charge)

class CouncilDeliberation(Act):
    final_id = ""
    execution_date = ""
    initiative = "" # (council_member, ...)

class CityGovernmentDeliberation(Act):
    pass

class Interrogation(Act):
    pass

class Interpellation(Act):
    pass

class Motion(Act):
    pass

class Agenda(Act):
    pass

class Emendation(Act):
    pass

class Attachment:
    description = ""
    file = None
    type = "" # type of file (define an array of possible file types)
    
# people section

class Person:
    id = ""
    name = ""
    surname = ""
    ssn = ""
    
    def __init__(self, id, name, surname, ssn):
        self.id = id
        self.name = name
        self.surname = surname
        self.ssn = ssn
        
    def __str__(self):
        return "%s %s (%s)" % (self.name, self.surname, self.id)
    
    def __unicode__(self):
        return u"%s %s (%s)" % (self.name, self.surname, self.id)

class Charge:
    id = ""
    start_date = ""
    person = None
    name = None
    description = ""
    
    def __init__(self, id, start_date, person, name, description):
        self.id = id
        self.start_date = start_date
        self.person = person
        self.name = name
        self.description = description
        
    def __str__(self):
        return "%s as %s from %s (%s)" % (self.person, self.name, self.start_date, self.id)
    
    def __unicode__(self):
        return u"%s as %s from %s (%s)" % (self.person, self.name, self.start_date, self.id)
    
# institution section
    
class Institution:    
    charges = []
    
    def add_charge(self, charge):
        self.charges.append(charge)
    
class Mayor(Institution):
    
    def __init__(self, mayor):
        self.append(mayor)

class CityGovernment(Institution):
    pass

class CityCouncil(Institution):
    pass
    
class Subscriber:
    charge = None
    type = "" # first subscriber or co-subscriber
    
