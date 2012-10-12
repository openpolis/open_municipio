from django.utils import simplejson as json

from open_municipio.data_import.lib import DataSource, BaseReader, BaseWriter, JSONWriter, XMLWriter, OMWriter
# import OM-XML language tags
from open_municipio.data_import.om_xml import *
from open_municipio.data_import import conf
from open_municipio.data_import.acts import conf as act_conf
from open_municipio.acts.models import Act as OMAct, Deliberation as OMDeliberation, Motion as OMMotion, Agenda as OMAgenda

from lxml import etree
from types import NoneType
from django.db.models import get_model

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
        
        self.acts = data_source.get_acts()
        
        # TODO extract the relevant information
        
        return self.acts;      


class BaseActsWriter(BaseWriter):
    """
    An abstract writer class that serializes internal representations 
    of acts-related data.
    
    This class encapsulates acts-specific serialization logic which is independent 
    from a specific output format. 
    """
    def __init__(self, acts):
        self.logger.info("Preparing to import %d acts into OM ..." % len(acts))
        self.acts = acts

class OMActsWriter(BaseActsWriter, OMWriter):
    """
    A writer class which outputs acts data as objects in the OpenMunicio model.
    """
#    emitting_institution = None
    
#    def set_emitting_institution(self, institution):
#        self.emitting_institution = institution
                            
    def write(self):
        for act in self.acts.values():
            try:
                self.write_act(act)
            except Exception, e:
                self.logger.error("Error storing act into OM (%s) : %s" % (act, e))
 
    @staticmethod
    def _get_initiative(act):
        if not act.initiative in act_conf.OM_DELIBERATION_INITIATIVE_MAP:
            raise Exception("Initiative string (%s) is not supported" % 
                act.initiative)
        return act_conf.OM_DELIBERATION_INITIATIVE_MAP[act.initiative]

    @staticmethod
    def _get_emitting_institution(act):

        act_type = act.__class__.__name__
        if not act_type in act_conf.OM_EMITTING_INSTITUTION_MAP:
            raise Exception("Act type not supported: %s" % act_type)

        return act_conf.OM_EMITTING_INSTITUTION_MAP[act_type]

   
    def write_act(self, act):
        
        act_obj_type = act.__class__.__name__
        self.logger.info("Writing act (id: %s, type %s)" % (act.id,act_obj_type))

        # dynamic instantiation of OM type
        om_type = NoneType
        if act_obj_type == "CouncilDeliberation":
            om_type = OMDeliberation
        elif act_obj_type == "Motion":
            om_type = OMMotion
        elif act_obj_type == "Agenda":
            om_type = OMAgenda

        if om_type == NoneType:
            self.logger.error("Unable to instantiate type: %s" %
                act_obj_type)
            return
        
#        self.logger.info("Type detected: %s" % om_type)

        om_emitting = OMActsWriter._get_emitting_institution(act)
        create_defaults={
                    'text' : act.content,
                    'emitting_institution': om_emitting,
                }
        if act.__class__.__name__ == "CouncilDeliberation":
            om_initiative = OMActsWriter._get_initiative(act)
            create_defaults['initiative'] = om_initiative
            self.logger.info("Set the initiative: %s" % om_initiative)

        self.logger.info("Piece of content: %s (type %s)" % (act.content[0:30], type(act.content)))
        (om_act, created) = om_type.objects.get_or_create(
                idnum = act.id, defaults = create_defaults )
        
        if created:
            self.logger.info("OM Act created %s" % act.id)
        else:
            self.logger.info("OM Act already present %s" % act.id)
    
# python object layer for imported data

# document section

class Act:
    id = ""
    content = ""
    title = ""
    file = None
    subscribers = [] # list of Charges
    emitting_institution = ""
    
    
    def add_subscriber(self, charge):
        self.subscribers.append(charge)
        
    def __str__(self):
        return "%s (%s) [%s]" % (self.title, self.id, self.content[0:20])
      
    def __unicode__(self):
      return u"%s (%s) [%s]" % (self.title, self.id, self.content[0:20])

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
    
