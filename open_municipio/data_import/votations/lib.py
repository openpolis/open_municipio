from django.utils import simplejson as json

from open_municipio.data_import.lib import DataSource, BaseReader, BaseWriter, JSONWriter, XMLWriter
# import OM-XML language tags
from open_municipio.data_import.om_xml import *

from lxml import etree, objectify
 
class VotationDataSource(DataSource):
    """
    A data source containing votation-related data.
    """
    def get_sittings(self):
        """
        Retrieves a list comprising all sittings provided by this data source
        (as ``Sitting`` instances).
        """  
        raise NotImplementedError
    
    def get_ballots(self, sitting):
        """
        Retrieves a list comprising all ballots of a given sitting
        (as ``Ballot`` instances).
        """
        raise NotImplementedError
    
    def get_votes(self, ballot):
        """
        Retrieves a list comprising all votes of a given ballot
        (as ``Vote`` instances).
        """
        raise NotImplementedError


## classes of "DOM" elements

class Sitting(object):
    def __init__(self, call=None, date=None, seq_n=None):
        # sitting instance attributes
        self.call = call         
        self.date =  date
        self.seq_n = seq_n
        # ballots comprising this sitting
        self.ballots = []
    
    def __repr__(self):
        return "Sitting #%(sitting_n)s of %(sitting_date)s" % {'sitting_n': self.seq_n, 'sitting_date': self.date}

class Ballot(object):
    def __init__(self, sitting, seq_n=None, timestamp=None, ballot_type=None, 
                 n_presents=None, n_partecipants=None, n_yes=None, n_no=None, n_abst=None, 
                 n_legal=None, outcome=None):
        # parent sitting
        self.sitting = sitting
        # ballot instance attributes
        self.seq_n = seq_n 
        self.time = timestamp
        self.type_ = ballot_type
        self.n_presents = n_presents
        self.n_partecipants = n_partecipants
        self.n_yes = n_yes
        self.n_no = n_no
        self.n_abst = n_abst
        self.n_legal = n_legal
        self.outcome = outcome
        # votes comprising this ballot
        self.votes = []

    def __repr__(self):
        return "Ballot #%(ballot_n)s of %(sitting)s" % {'ballot_n': self.seq_n, 'sitting': self.sitting}

class Vote(object):
    def __init__(self, ballot, cardID=None, componentID=None, groupID=None, component_name=None, choice=None):
        # parent ballot
        self.ballot = ballot
        # vote instance attributes
        self.cardID = cardID 
        self.componentID = componentID
        self.groupID = groupID
        self.choice = choice
        
    def __repr__(self):
        return "Vote of %(component_ID)s in %(ballot)s" % {'component_ID': self.componentID, 'ballot': self.ballot} 


class BaseVotationReader(BaseReader):
    """
    An abstract reader class parsing votation-related data.
    
    This class encapsulates generic -- but votation-specific -- parsing logic. 
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
        self.sittings = []
        # construct the DOM tree
        for sitting in data_source.get_sittings():
            sitting.ballots = data_source.get_ballots(sitting)
            for ballot in sitting.ballots:
                ballot.votes = data_source.get_votes(ballot)
            self.sittings.append(sitting)
        # as now, ``self.sittings`` should be a object tree 
        # providing a comprehensive representation of all relevant data
        # that can be extracted from the data source
        return self.sittings      

    
class GenericVotationReader(BaseVotationReader):
    pass


class BaseVotationWriter(BaseWriter):
    """
    An abstract writer class that serializes internal representations 
    of votation-related data.
    
    This class encapsulates votation-specific serialization logic which is independent 
    from a specific output format. 
    """
    def __init__(self, sittings):
        self.sittings = sittings

    
class JSONVotationWriter(BaseVotationWriter, JSONWriter):
    """
    A writer class which outputs votations data as a JSON data structure.
    
    Useful for testing purposes. 
    """
    def write(self):
        return json.dumps(self.sittings)
    

class XMLVotationWriter(BaseVotationWriter, XMLWriter):
    """
    A writer class which outputs votations data as an XML document, 
    according to the OM-XML schema specs.
    
    So, its output can be imported directly into a running instance of OpenMunicipio.
    """
                
    def write(self):
        ## build XML element tree
        root = SITTINGS()
        root.set(XSI+'schemaLocation', OMXML_SCHEMA_LOCATION)
        for sitting in self.sittings[:-1]:
            root.append(SITTING(
                                call=str(sitting.call), 
                                date=str(sitting.date), 
                                num=str(sitting.seq_n))
                                )
            for ballot in sitting.ballots[:3]:
                root.Sitting[-1].append(VOTATION(
                                                 seq_n=ballot.seq_n,
                                                 votation_type=ballot.type_,
                                                 presents=ballot.n_presents,
                                                 partecipants=ballot.n_partecipants,
                                                 outcome=ballot.outcome,
                                                 legal_number=ballot.n_legal,
                                                 date_time=ballot.time,
                                                 counter_yes=ballot.n_yes,
                                                 counter_no=ballot.n_no,
                                                 counter_abs=ballot.n_abst,                                                                                                    
                                                 SUBJECT(sintetic='', ''), 
                                                 VOTES()))
                for vote in ballot.votes[:3]:
                    root.Sitting[-1].Votation[-1].Votes.append(CHARGEVOTE(
                                                                          cardID=vote.cardID,
                                                                          componentID=vote.componentID,
                                                                          groupID=vote.groupID,
                                                                          vote=vote.choice,
                                                                          CHARGEXREF().set(XLINK+'href', '').set(XLINK+'type', 'simple')                                                                                 
                                                                                     ))
        ## serialize generated element tree to a string
        out_xml =  etree.tostring(root, pretty_print=True)
        return out_xml   