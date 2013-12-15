import os
import traceback

from django.core.files import File
from django.core.exceptions import ObjectDoesNotExist
from django.utils import simplejson as json
from django.db.utils import IntegrityError
from django.db import transaction, models

from open_municipio.data_import.lib import DataSource, BaseReader, BaseWriter, JSONWriter, XMLWriter, OMWriter
# import OM-XML language tags
from open_municipio.data_import.om_xml import *
from open_municipio.data_import import conf
from open_municipio.data_import.acts import conf as act_conf
from open_municipio.data_import.utils import ChargeSeekerFromMapMixin

from open_municipio.acts.models import Act as OMAct, \
    Deliberation as OMDeliberation, Motion as OMMotion, Agenda as OMAgenda, \
    ActSupport as OMActSupport, Attach as OMAttach, Transition as OMTransition, \
    CGDeliberation as OMCGDeliberation

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

    def setup(self):
        self.conf = conf

    @transaction.commit_on_success
    def write(self):
        self.logger.info("Acts to write: %d" % len(self.acts.values()))
        for act in self.acts.values():
            try:
                self.write_act(act)
            except Exception, e:
                self.logger.error(u"Error storing act into OM (%s) : %s. Trace: %s" % (act, e, traceback.format_exc()))
                transaction.rollback()
 
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
        
        assert isinstance(act, Act)
        
        act_obj_type = act.__class__.__name__

        # dynamic instantiation of OM type
        
#        om_type = NoneType
#        if act_obj_type == "CouncilDeliberation":
#            om_type = OMDeliberation
#        elif act_obj_type == "Motion":
#            om_type = OMMotion
#        elif act_obj_type == "Agenda":
#            om_type = OMAgenda
#        elif act_obj_type == "CityGovernmentDeliberation":
#            om_type = OMCGDeliberation
        om_type = act_conf.OM_ACT_MAP.get(act_obj_type, NoneType)
        

        if om_type == NoneType:
            self.logger.error("Unable to instantiate type: %s" %
                act_obj_type)
            return
        
#        self.logger.info("Type detected: %s" % om_type)

        return om_type
  
    def _add_act_transition(self, act, om_act, symb):
        if om_act is None:
            raise ValueError("Cannot add act transition without act")

        for date in act.transitions[symb]:
            if not (symb in conf.XML_TO_OM_STATUS):
                self.logger.warning("Status '%s' is not handled at the moment. Skip the transition" % symb)
                continue
    
            status = conf.XML_TO_OM_STATUS[symb]
            (om_t, created) = OMTransition.objects.get_or_create(
                act=om_act, symbol=symb, transition_date=date, final_status=status
            )
            
            if created:
                self.logger.debug("New transition found. Act=%s,Symbol=%s,Date=%s" % (act.title,symb,date))
                self._set_act_status(om_t)
                om_t.save()
    

    def _add_act_transitions(self, act, om_act):
        if om_act is None:
            raise ValueError("Cannot add act transitions without act")
        order_symb = ( "Presented", "Accepted", "Rejected", )

        self.logger.info("Transition dates: %s" % (act.transitions, ))
        if act.transitions == None:
            return

        for symb in order_symb:
            if symb in act.transitions:
                self._add_act_transition(act, om_act, symb)

        # check whether transitions with other symbols are present
        keyset_actual = set(act.transitions.keys())
        keyset_handled = set(order_symb)

        keyset_nothandled = keyset_actual.difference(keyset_handled)
        if keyset_nothandled != set():
            self.logger.warning("Some transitions are not handled: %s" %
                keyset_nothandled)

    def _set_act_status(self, om_trans):

        om_act = om_trans.act

        if om_act.is_final_status():
            # cannot recover from a final status
            self.logger.debug("Ignore transition status (%s). Act status is already final (%s)" % (om_trans.final_status, om_act.status))
            return

        self.logger.debug("Set act status: %s" % om_trans.final_status)
        om_act.status = om_trans.final_status


    def _init_act_create_defaults(self, act):
        
        assert isinstance(act, Act)
        
        act_obj_type = act.__class__.__name__

        om_emitting = OMActsWriter._get_emitting_institution(act)

        create_defaults = {
                    'idnum' : act.id,
                    'title' : act.title,
                    'text' : act.content,
                    'emitting_institution': om_emitting,
                    'presentation_date' : None,
                    'transitions' : None,
                }

        pdate = self.load_transition_date(act.transitions, "Presented")
        if pdate:
            create_defaults["presentation_date"] = pdate

        adate = self.load_transition_date(act.transitions, "Accepted")
        if adate and act_obj_type in ["CouncilDeliberation","CityGovernmentDeliberation",]:
            create_defaults["approval_date"] = adate

        if act_obj_type == "CouncilDeliberation":
            om_initiative = OMActsWriter._get_initiative(act)
            create_defaults['initiative'] = om_initiative
            self.logger.info("Set the initiative: %s" % om_initiative)

            create_defaults['final_idnum'] = act.final_id
            self.logger.info("Set the final_idnum: %s" % act.final_id)
        elif act_obj_type == "Amendment":
            try:
                referred_act = OMDeliberation.objects.get(
                                    models.Q(idnum=act.referred_act) |
                                    models.Q(final_idnum=act.referred_act))
                create_defaults["act"] = referred_act
            except ObjectDoesNotExist:
                self.logger.error("Unable to find referred act (%s) for amendment (%s)" % (act.referred_act, act.id))


        self.logger.debug("Act presentation date: %s" % create_defaults["presentation_date"])

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

    def load_transition_date(self, transitions, label):
        if label in transitions:
            # the presentation date is unique, take the first item
            self.logger.debug("%s dates: %s" % (label, transitions[label],))
            date = transitions[label][0]
            self.logger.debug("label=%s date found: %s" % (label, date, )) 

            return date
        else:
            self.logger.debug("label=%s date not found" % label)
            return None



    @transaction.commit_on_success
    def _add_attachments(self, act, om_act):
        if act == None or om_act == None:
            raise Exception("Cannot add an attachment if you don't pass both the parsed act and the partially imported OM act.")

        self.logger.info("Attachments to add: %d" % len(act.attachments))
        for curr_att in act.attachments:
            self.logger.info("Processing attachment file %s" % curr_att.path)
            f = File(open(curr_att.path))

            found_att = OMAttach.objects.filter(act=om_act, \
                document_type=curr_att.type, document_date=curr_att.document_date)

            if found_att.count() > 0:
                self.logger.info("Attachment already present: %s" % curr_att.path)
            else:
                defaults = {
                    'file' : f,
                    'act' : om_act,
                    'document_type' : curr_att.type,
                    'document_size' : f.size,
                    'title' : curr_att.title[:512], # TODO parameterize this length
                    'document_date' : curr_att.document_date,
                }
                om_attachment = OMAttach(**defaults)
                try:
                    om_attachment.save()
                    self.logger.info("Attachment imported correctly: %s" % 
                        curr_att.path)
                except Exception as e:
                    self.logger.warning("Error importing attachment %s: %s" % 
                        (curr_att.path, e))
                    transaction.rollback()

    def _add_subscribers(self, act, om_act):
        """
        Assign the subscribers as represented in act, to the om_act instance.
        Remember that om_act is an instance of (a subtype of) the Act model,
        while act is an instance of the "intermediate" representation.
        
        Adding the subscriber, we use the get_or_create method, so that no
        duplicates are produced (e.g. in case the same data is first manually
        inserted, and later automatically imported) 
        """
        
        assert isinstance(act, Act)
        assert isinstance(om_act, OMAct)
        
        if act == None or om_act == None:
            raise Exception("Cannot add the subscribers if you don't pass both the parsed act and the partially imported OM act.")

        if om_act.emitting_institution is None:
            raise Exception("The partially imported OM act is malformed: missing emitting institution")
            return

        if self.conf.ACTS_PROVIDER == None:
            self.logger.warning("In order to continue, you must set a data provider for charges in act importation")
            return

        self.logger.debug("Reset subscribers of act %s ..." % (om_act, ))
        # delete previous supporter for the act (ASSUMPTION: the imported data are complete and correct)
        #OMActSupport.objects.filter(act = om_act).delete()
        #om_act.presenter_set.delete()
        OMActSupport.objects.filter(act=om_act).delete()

        for curr_sub in act.subscribers:
            act_date = getattr(act, "presentation_date", None)
            
            om_ch = self.lookup_charge(curr_sub.charge.id, self.conf.ACTS_PROVIDER, act_date)

            if om_ch is None:
#                raise Exception("Unable to find charge for %s as of %s" % (curr_sub, act_date, ))
                self.logger.warning("Unable to find charge for %s as of %s" % (curr_sub, act_date, ))
                continue
            else:
                self.logger.info("Charge for subscriber: %s (was %s) as of %s ..." % (om_ch,curr_sub.charge.id, act_date,))

            # detect support type
            om_support_type = OMActSupport.SUPPORT_TYPE.co_signer
            if curr_sub.type == "first_subscriber":
                om_support_type = OMActSupport.SUPPORT_TYPE.first_signer
            #self.logger.info("Mapping subscriber type: %s -> %s" % (curr_sub.type,om_support_type))

            create_defaults = self._init_subscriber_create_defaults(om_act, om_ch,
                om_support_type)

            #(om_sub, created) = OMActSupport.objects.get_or_create(
            #    act = om_act, charge = om_ch, defaults = create_defaults
            #)
            try:
                om_sub = OMActSupport(**create_defaults)
                om_sub.save()
                self.logger.info("Added charge %s as subscriber ..." % om_ch)
            except Exception, e:
                self.logger.warning("Error setting charge %s as subscriber for act %s: %s ..."
                    % (om_act, om_ch, e))

        n_subs_read = len(act.subscribers)
        n_subs_written = om_act.presenter_set.count()
        if n_subs_read != n_subs_written:
            self.logger.warning("Something wrong happened importing subscribers: %s read, %s written ..."
                    % (n_subs_read, n_subs_written, ))
        

    def update_act(self, om_act, dict_values):

        if om_act is None:
            raise ValueError("Instance you want to update should not be None")

        for (k, v) in dict_values.items():
            # don't update if the field is None (or you risk to delete data)
            if v is not None:
                self.logger.debug("Update field: %s <- %s" % (k,v,))
                setattr(om_act, k, v)

        om_act.save()

    def write_act(self, act):
        
        assert isinstance(act, Act)
        
        act_obj_type = act.__class__.__name__
        self.logger.info("Writing act (id: %s, type %s)" % (act.id,act_obj_type))

        create_defaults = self._init_act_create_defaults(act)

        #self.logger.info("Piece of content: %s ..." % act.content[0:30])
#        self.logger.info("Defaults: %s ..." % create_defaults)

        om_type = self._detect_act_om_type(act)
        self.logger.info("Detected type %s" % om_type)

        # TODO create the act and the subscribers as a transaction
        (om_act,created) = om_type.objects.get_or_create(idnum=act.id,
            defaults = create_defaults)

        if created:
            self.logger.info("OM act  %s created ..." % om_act.idnum)
        else:
            self.update_act(om_act, create_defaults)
            self.logger.info("OM act  %s updated ..." % om_act.idnum)

        self.logger.info("Now let's add the attachment ...")
        self._add_attachments(act, om_act)

        # append transitions to acts on OM
        self._add_act_transitions(act, om_act)

                
        self.logger.info("Set the act supporters ...")
        self._add_subscribers(act, om_act)

        

# python object layer for imported data

# document section

class Act:
    id = ""
    content = ""
    title = ""
    file = None
#    presentation_date = None
    subscribers = [] # list of Charges
    emitting_institution = ""
    attachments = [] # list of Attachment (usually one is enough ...)

    transitions = {} # transitions are stored by their symbol. every symbol can
                     # contain one or more transition dats
    
    
    def add_subscriber(self, charge):
        self.subscribers.append(charge)
        
    def __str__(self):
        return "%s (%s) [%s]" % (self.title, self.id, self.content[0:20])
      
    def __unicode__(self):
      return u"%s (%s) [%s]" % (self.title, self.id, self.content[0:20])

class CouncilDeliberation(Act):
    final_id = None
#    execution_date = None
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

class Amendment(Act):
    
    # a reference to the amended act
    referred_act = None

class Attachment:
    description = ""
    file = None
    type = "" # type of file (define an array of possible file types)
    title = ""
    document_date = None

    def __init__(self, path, description=None, type=None):
        if path == "":
            raise Exception("It is not possible to specify an empty path as attachment")
        if not os.path.exists(path):
            raise Exception("The specified attachment path %s does not exist" % path)
        self.path = path
        self.description = description
        self.type = type

    
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
