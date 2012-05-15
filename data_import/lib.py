from django.utils import simplejson as json
from django.core.exceptions import ImproperlyConfigured

## classes of "DOM" elements

class Sitting(object):
    def __init__(self, call=None, date=None, seq_n=None):
        # sitting instance attributes
        self.call = call         
        self.date =  date
        self.seq_n = seq_n
        # ballots comprising this sitting
        self.ballots = []


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
        

class Vote(object):
    def __init__(self, ballot, cardID=None, componentID=None, groupID=None, choice=None):
        # parent ballot
        self.ballot = ballot
        # vote instance attributes
        self.cardID = cardID 
        self.componentID = componentID
        self.groupID = groupID
        self.choice = choice


class BaseReader(object):
    """
    Reads from a data source and returns a parsed, internal representation of the data
    contained within that source.
    
    This an abstract base class, encapsulating generic parsing logic. 
    It's intended to be subclassed (and its methods overriden) in order to adapt to 
    concrete scenarios. 
    
    In this context, the meaning of *data source* is implementation-dependent: 
    a data source may be a file, a directory of files, a URLs, a generic stream, etc.
    """
    def __init__(self, data_source=None):
        self.data_source = data_source
    
    def get_data_source(self):
        """
        Return an object representing the data source to read from. 
        
        This base implementation returns the ``data_source`` instance attribute, if set;
        otherwise, raises an ``ImproperlyConfigured`` exception. 
        """   
        if self.data_source:
            return self.data_source
        else:
            raise ImproperlyConfigured("You must provide a data source")  
        
    def read(self):
        raise NotImplementedError

    
class BaseVotationReader(BaseReader):
    """
    An abstract reader class parsing votation-related data.
    
    This class encapsulates generic -- but votation-specific -- parsing logic. 
    It's intended to be subclassed (and its methods overriden) in order to adapt to 
    concrete scenarios. 
    """
    def read(self):
        for sitting in self.get_sittings():
            sitting.ballots = self.get_ballots(sitting)
            for ballot in sitting.ballots:
                ballot.votes = self.get_votes(ballot)
        
        # as now, ``self.sittings`` should be a object tree 
        # providing a comprehensive representation of all relevant data
        # that can be extracted from the data source
        return self.sittings       
    
    def get_sittings(self):
        """
        Retrieve a list comprising all sittings provided by the data source.
        """  
        raise NotImplementedError
    
    def get_ballots(self, sitting):
        """
        Retrieve a list comprising all ballots of a given sitting.
        """
        raise NotImplementedError
    
    def get_votes(self, ballot):
        """
        Retrieve a list comprising all votes of a given ballot.
        """
        raise NotImplementedError


    
class GenericVotationReader(BaseVotationReader):
    pass
    
    
class BaseWriter(object):
    """
    Serializes a given data structure to a specific output format.
    
    The data structure is usually (but not necessarily) a tree of Python objects,
    while the output format is some kind of string representation of that 
    internal data structure.
    
    This an abstract base class, encapsulating generic serialization logic. 
    It's intended to be subclassed (and its methods overriden) in order to 
    provide support for a given serialization format.
    """
    def __init__(self, data):
        self.data = data
        
    def write(self):
        raise NotImplementedError


class BaseVotationWriter(BaseWriter):
    """
    An abstract writer class that serializes internal representations 
    of votation-related data.
    
    This class encapsulates votation-specific serialization logic which is independent 
    from a specific output format. 
    """
    def __init__(self, sittings):
        self.sittings = sittings

    
class JSONVotationWriter(BaseVotationWriter):
    """
    A writer class which outputs votations data as a JSON data structure.
    
    Useful for testing purposes. 
    """
    def write(self):
        return json.dumps(self.sittings)
    

class XMLVotationWriter(BaseVotationWriter):
    """
    A writer class which outputs votations data as a XML document, 
    according to the OM-XML schema specs.
    
    So, its output can be imported directly into a running instance of OpenMunicipio.
    """
    raise NotImplementedError