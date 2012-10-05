from django.utils import simplejson as json
from open_municipio.data_import.lib import DataSource, BaseReader, BaseWriter, JSONWriter, XMLWriter, valid_XML_char_ordinal
# import OM-XML language tags
from open_municipio.data_import.om_xml import *
# import models used in DBVotationWriter
from open_municipio.people.models import Institution
from open_municipio.votations.models import Sitting as DBSitting
from open_municipio.votations.models import Votation as DBBallot
from open_municipio.votations.models import ChargeVote as DBVote

from lxml import etree

import logging

 
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
    def __init__(self, call=None, date=None, seq_n=None, site=None):
        # sitting instance attributes
        self.call = call         
        self.date =  date
        self.seq_n = seq_n
        self.site = site
        # ballots comprising this sitting
        self.ballots = []
    
    def __repr__(self):
        return "Sitting #%(sitting_n)s of %(sitting_date)s" % {'sitting_n': self.seq_n, 'sitting_date': self.date}

class Ballot(object):
    def __init__(self, sitting, seq_n=None, timestamp=None, ballot_type=None, short_subj=None, subj=None,
                 n_presents=None, n_partecipants=None, n_majority=None, n_yes=None, n_no=None, n_abst=None,
                 n_legal=None, outcome=None):
        # parent sitting
        self.sitting = sitting
        # ballot instance attributes
        self.seq_n = seq_n 
        self.time = timestamp
        self.type_ = ballot_type
        self.short_subj = short_subj
        self.subj = subj
        self.n_presents = n_presents
        self.n_partecipants = n_partecipants
        self.n_majority = n_majority
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

class DBVotationWriter(BaseVotationWriter):

    logger = logging.getLogger('import')

    def setup(self):
        self.conf = None


    def write_vote(self, vote, db_ballot=None):
        raise Exception("Not implemented")

    def write(self):
        self.setup()

        for sitting in self.sittings:
            self.logger.debug("processing %s in Mdb" % sitting)
            inst = Institution.objects.get(name=self.conf.XML_TO_OM_INST[sitting.site])

            s, created = DBSitting.objects.get_or_create(
                idnum=sitting._id,
                defaults={
                    'number':      sitting.seq_n,
                    'date':        sitting.date,
                    'call':        sitting.call,
                    'institution': inst,
                    }
            )
            if created:
                self.logger.info("%s created in DB" % s)
            else:
                self.logger.debug("%s found in DB" % s)

            for ballot in sitting.ballots:
                self.logger.debug("processing %s in Mdb" % ballot)

                # get or create the sitting in the DB
                b, created = DBBallot.objects.get_or_create(
                    idnum=int(ballot.seq_n),
                    sitting=s,
                    defaults={
                        'act_descr': ballot.subj or ballot.short_subj or "",
                        'n_legal': int(ballot.n_legal),
                        'n_presents': int(ballot.n_presents),
                        'n_partecipants': int(ballot.n_partecipants),
                        'n_maj': int(ballot.n_majority),
                        'n_yes': int(ballot.n_yes),
                        'n_no': int(ballot.n_no),
                        'n_abst': int(ballot.n_abst),
                        'outcome': int(ballot.outcome),
                    }
                )
                if created:
                    self.logger.debug("%s created in DB" % b)
                else:
                    self.logger.debug("%s found in DB" % b)

                for vote in ballot.votes:
                    self.logger.debug("processing %s in Mdb" % vote)
                    self.write_vote(vote, db_ballot=b)

                # update votation caches
                b.update_caches()
                self.logger.debug("caches for this votation updated.\n")


class XMLVotationWriter(BaseVotationWriter, XMLWriter):
    """
    A writer class which outputs votations data as an XML document, 
    according to the OM-XML schema specs.
    
    So, its output can be imported directly into a running instance of OpenMunicipio.
    """

    def setup(self):
        self.conf = None

    def write(self):
        self.setup()

        for sitting in self.sittings:
            out_fname = self.get_out_fname(sitting)
            tree = self.write_sitting(sitting)
            tree.write(out_fname, 
                       pretty_print=True, 
                       xml_declaration=True, 
                       encoding='UTF-8')
            
    def write_sitting(self, sitting):
        """
        Returns the XML representation (as a ``ElementTree`` object) of a given City Council sitting.
        """   
        ## build XML element tree
        root = SITTINGS()
        root.set(XSI + 'schemaLocation', OMXML_SCHEMA_LOCATION)
    
        sitting_el = SITTING()
        attrs = dict(call=sitting.call,
                     date=sitting.date,
                     num=sitting.seq_n,
                     site=sitting.site)
        self._set_element_attrs(sitting_el, attrs)
        root.append(sitting_el) 
        for ballot in sitting.ballots:
            ballot_el = VOTATION(SUBJECT(ballot.subj, sintetic=ballot.short_subj), VOTES())
            attrs = dict(seq_n=ballot.seq_n,
                         votation_type=ballot.type_,
                         presents=ballot.n_presents,
                         partecipants=ballot.n_partecipants,
                         majority=ballot.n_majority,
                         outcome=self.conf.OUTCOMES[int(ballot.outcome)],
                         legal_number=ballot.n_legal,
                         date_time=ballot.time,
                         counter_yes=ballot.n_yes,
                         counter_no=ballot.n_no,
                         counter_abs=ballot.n_abst,)
            self._set_element_attrs(ballot_el, attrs) 
            sitting_el.append(ballot_el)
            for vote in ballot.votes:
                vote_el = CHARGEVOTE()
                attrs = dict(cardID=vote.cardID,
                                    componentID=vote.componentID,
                                    groupID=vote.groupID,
                                    vote=self.conf.XML_TO_OM_VOTE[vote.choice],
                                    component_name=vote.componentName)
                self._set_element_attrs(vote_el, attrs)
                ballot_el.append(vote_el)
                chargexref_el = CHARGEXREF()
                attrs = {
                         XLINK + 'href': vote.componentID,
                         XLINK + 'type': 'simple',
                        }
                self._set_element_attrs(chargexref_el, attrs)
                vote_el.append(chargexref_el)
        return etree.ElementTree(root)
    
    def get_out_fname(self, sitting):
        """
        Returns the absolute filesystem path where to store the XML document 
        containing data related to a given sitting of the City Council.
        """
        raise NotImplementedError