import traceback
from django.core.exceptions import ObjectDoesNotExist
from django.utils import simplejson as json
from django.db.utils import IntegrityError
from django.db import transaction

from open_municipio.data_import.lib import DataSource, BaseReader, BaseWriter, JSONWriter, XMLWriter, OMWriter
# import OM-XML language tags
from open_municipio.data_import.om_xml import *
from open_municipio.data_import import conf
from open_municipio.data_import.acts import conf as act_conf
from open_municipio.data_import.models import ChargeSeekerFromMapMixin

from open_municipio.acts.models import Act as OMAct, \
    Deliberation as OMDeliberation, Motion as OMMotion, Agenda as OMAgenda, \
    ActSupport as OMActSupport

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

class OMActsWriter(ChargeSeekerFromMapMixin, BaseActsWriter, OMWriter):
    """
    A writer class which outputs acts data as objects in the OpenMunicio model.
    """
    
    @transaction.commit_on_success
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

    def _detect_act_om_type(self, act):
        act_obj_type = act.__class__.__name__

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

        return om_type
  

    def _init_act_create_defaults(self, act):
        act_obj_type = act.__class__.__name__

        om_emitting = OMActsWriter._get_emitting_institution(act)

        create_defaults = {
                    'idnum' : act.id,
                    'text' : act.content,
                    'emitting_institution': om_emitting,
                    'transitions' : None
                }

        if act_obj_type == "CouncilDeliberation":
            om_initiative = OMActsWriter._get_initiative(act)
            create_defaults['initiative'] = om_initiative
            self.logger.info("Set the initiative: %s" % om_initiative)

        return create_defaults
   
    def _init_subscriber_create_defaults(self, om_act, om_charge, type, date=None):
        create_defaults = {
            'charge' : om_charge,
            'act' : om_act,
            'support_type' : type,
        }

        if date != None:
            create_defaults['support_date'] = date

        return create_defaults

    def _add_subscribers(self, act, om_act):

        if act == None or om_act == None:
            raise Exception("Cannot add the subscribers if you don't pass both the parsed act and the partially imported OM act.")

        if om_act.emitting_institution is None:
            raise Exception("The partially imported OM act is malformed: missing emitting institution")

        for curr_sub in act.subscribers:
            om_ch = self.lookup_charge(curr_sub.charge.id)

            if om_ch is None:
                raise Exception("Unable to find charge for %s" % curr_sub)

            self.logger.info("Charge for subscriber: %s (was %s) ..." % (om_ch,curr_sub.charge.id))

            # detect support type
            om_support_type = OMActSupport.SUPPORT_TYPE.co_signer
            if curr_sub.type == "first_subscriber":
                om_support_type = OMActSupport.SUPPORT_TYPE.first_signer
            self.logger.info("Mapping subscriber type: %s -> %s" % (curr_sub.type,om_support_type))

            create_defaults = self._init_subscriber_create_defaults(om_act, om_ch,
                om_support_type)

            (om_sub, created) = OMActSupport.objects.get_or_create(
                act = om_act, charge = om_ch, defaults = create_defaults
            )

            if created:
                self.logger.info("Added charge %s as subscriber ..." % om_ch)
            else:
                self.logger.info("Charge %s already known to be a subscriber ..."
                    % om_ch)

    def write_act(self, act):
        
        act_obj_type = act.__class__.__name__
        self.logger.info("Writing act (id: %s, type %s)" % (act.id,act_obj_type))

        create_defaults = self._init_act_create_defaults(act)

        self.logger.info("Piece of content: %s ..." % act.content[0:30])
#        self.logger.info("Defaults: %s ..." % create_defaults)

        om_type = self._detect_act_om_type(act)
        self.logger.info("Detected type %s" % om_type)
        # TODO create the act and the subscribers as a transaction

        created = False
        try:
            om_act = om_type.objects.get(idnum=act.id)
            self.logger.info("Act already present ...")
        except ObjectDoesNotExist:
            self.logger.info("Act needs to be created ...")
            om_act = om_type(**create_defaults)
            try:
                om_act.save()
                created = True
            except IntegrityError as ex:
# TODO this exception should be fixed!!! - FS
                self.logger.warning("Act saved. Integrity error: %s" % ex)
                self.logger.warning("Integrity error trace: %s" % 
                    traceback.format_exc())
                created = True
            except Exception as ex:
                self.logger.error("Act may not be saved. Error (%s): %s" % 
                    (type(ex),ex))

#        (om_act, created) = om_type.objects.get_or_create(
#                idnum = act.id, defaults = create_defaults )
#        
        if created:
            self.logger.info("OM act created %s. Let's add the subscribers ..." % om_act.idnum)
            self._add_subscribers(act, om_act)

        else:
            self.logger.info("OM act already present %s" % om_act.idnum)



    
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
#    person = None
    charge = None
    name = None
    description = ""
    
    def __init__(self, id, start_date, charge, name, description):
        self.id = id
        self.start_date = start_date
#        self.person = person
        self.charge = charge
        self.name = name
        self.description = description
        
    def __str__(self):
#        return "%s as %s from %s (%s)" % (self.person, self.name, self.start_date, self.id)
        return "%s as %s from %s (%s)" % (self.charge, self.name, \
            self.start_date, self.id)
    
    def __unicode__(self):
#        return u"%s as %s from %s (%s)" % (self.person, self.name, self.start_date, self.id)
        return u"%s as %s from %s (%s)" % (self.charge, self.name, \
            self.start_date, self.id)
    
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
#    person = None
    type = "" # first subscriber or co-subscriber
 
#    def __init__(self, person, type):
#        self.person = person
#        self.type = type
#
    def __init__(self, charge, type):
        self.charge = charge
        self.type = type

    def __str__(self):
#        return "%s (%s)" % (self.person, self.type)
        return "%s (%s)" % (self.charge, self.type)

    def __unicode__(self):
#        return u"%s (%s)" % (self.person, self.type)
        return u"%s (%s)" % (self.charge, self.type)
