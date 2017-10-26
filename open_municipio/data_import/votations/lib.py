from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.utils import simplejson as json
from django.db import transaction
import re
from open_municipio.acts.models import Act
from open_municipio.data_import.lib import DataSource, BaseReader, BaseWriter, JSONWriter, XMLWriter, valid_XML_char_ordinal
# import OM-XML language tags
from open_municipio.data_import.om_xml import *
# import models used in DBVotationWriter
from open_municipio.people.models import Institution, municipality
from open_municipio.votations.models import Sitting as OMSitting, GroupVote
from open_municipio.votations.models import Votation as OMBallot
from open_municipio.votations.models import ChargeVote


from lxml import etree

import logging
import traceback

 
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

class SittingItem(object):
    def __init__(self, sitting_n=None, call=None, date=None, seq_n=None, site=None, n_votes=0):
        # sitting instance attributes
        self.sitting_n = sitting_n
        self.call = call         
        self.date =  date
        self.seq_n = seq_n
        self.site = site
        # ballots comprising this sitting
        self.ballots = []
        self.n_votes = n_votes
    
    def __repr__(self):
        return "SittingItem %s of Sitting %s, on date %s" % \
            ( self.seq_n, self.sitting_n, self.date )

class Ballot(object):
    def __init__(self, sitting, seq_n=None, timestamp=None, ballot_type=None, 
                short_subj=None, subj=None, n_presents=None, n_partecipants=None,
                n_majority=None, n_yes=None, n_no=None, n_abst=None,
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
        all_sittings = data_source.get_sittings()
        
        
        
        for sitting_item in all_sittings:
            assert isinstance(sitting_item, SittingItem)
            
            self.logger.debug("Sitting Item: %s, n_votes = %s" % (sitting_item, sitting_item.n_votes, ))
            if sitting_item.n_votes == 0:
                continue
            
            try:
                sitting_item.ballots = data_source.get_ballots(sitting_item)
                self.sittings.append(sitting_item)
            except Exception, e:
                self.logger.warning("Sitting %s has been skipped because of the following error: %s" % (sitting_item, e))

        #self.logger.info("Sittings with ballots: %s" % (self.sittings,))

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
    def __init__(self, sittings, **options):
        self.sittings = sittings
        self.options = options

    
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
        self.logger.info("Base setup...")
        self.conf = None

    def compute_absences(self, votation):
        """
        A charge is considered absent if she is a member of
        the Institution where the Votation took place,
        at the moment when the Votation took place,
        and her ChargeVote is not among the associate chargevote_set
        """
        votation_moment = votation.sitting.date.strftime('%Y-%m-%d')
        charges = votation.sitting.institution.get_current_charges(moment=votation_moment)
        self.logger.debug("Charges at date (%s): %s" % (votation_moment, 
                ",".join(map(lambda c: c.person.full_name, charges))))
    
        for c in charges:
            try:
                cv = votation.chargevote_set.get(charge__pk=c.pk)
            except ObjectDoesNotExist:
                # get or create absence ChargeVote in OpenMunicipio DB
                cv, created = ChargeVote.objects.get_or_create(
                    charge=c,
                    votation=votation,
                    vote=ChargeVote.VOTES.absent
                )
                self.logger.debug("Add absent ChargeVote: %s ..." % c)
            except MultipleObjectsReturned, e:
                self.logger.warning("Multiple vote from single charge. Votation: %s, charge: %s, charge pk: %s, error: %s. Continue ..." % (votation, c, c.pk, e))

        # update n_absents for the whole votation
        votation.n_absents = votation.charge_votes.filter(vote=ChargeVote.VOTES.absent).count()
        votation.save()

    def update_rebel_caches(self, votation):
        """
        Computes and update caches for the passed votation.

        Firstly, the group votes are computed and stored,
        then the rebel votes, and presence data are cached,
        both for the votation and the charge.

        A ChargeVote must be marked as ``rebel`` when her vote is different
        from that of her group.

        The ``rebel`` field can be assigned only if the counselor is present and
         if her group's vote is clearly defined (i.e., it is not *Not Avaliable*)

        This is only valid for council votations.

        After a rebel vote has been set, the following *caches* should be updated:

        * Votation.n_rebels - counts the total number of rebels for that votation
        """


        # compute rebel caches for each voting charge
        for vc in votation.charge_votes:
            group = vc.charge_group_at_vote_date
            if group is not None:
                charge_vote = vc.vote
                try:
                    group_vote = group.groupvote_set.get(votation=votation).vote
                    # check rebellion: if charge_vote is different from a significative group_vote
                    if charge_vote == ChargeVote.VOTES.yes or\
                       charge_vote == ChargeVote.VOTES.no or\
                       charge_vote == ChargeVote.VOTES.abstained:
                        if group_vote != GroupVote.VOTES.noncomputable and group_vote != charge_vote:
                            # add rebel status to ChargeVote
                            vc.is_rebel = True
                            vc.save()

                            # there's a new rebellion!
                            # votation and charge caches must be updated

                            # update charge cache
                            vc.charge.update_rebellion_cache()

                            # update votation cache
                            votation.n_rebels = votation.charge_votes.filter(is_rebel=True).count()
                            votation.save()
                except ObjectDoesNotExist:
                    pass


    def compute_group_votes(self, votation):
        """
        once all charges' votes have been stored,
        groups' votes are stored in GroupVote.vote

        A GroupVote is the same as the majority of the group.
        Whenever there is no clear majority (50%/50%), then a
        Not Available vote can be assigned to the Group.

        Other cached values are computed and stored in GroupVote, as well:
        * n_presents
        * n_yes
        * n_no
        * n_abst
        * n_rebels
        * n_absents
        """

        isinstance(votation, OMBallot)

        # reset: remove all GroupVotes for this votation,
        # so that group votes are never counted more than once
        votation.group_votes.delete()

        for cv in votation.charge_votes:

            if cv.charge.person == municipality.mayor.as_charge.person:
                # skip the mayor, he/she does not belong to any group
                # note that the mayor has 2 charges: as mayor and as counselor; for
                # this reason we check the person linked to the charge
                continue

            g = cv.charge_group_at_vote_date

            v = cv.vote

            if g is None:
                if v != ChargeVote.VOTES.absent and v != ChargeVote.VOTES.abstained:
                    # something is wrong: a person without a charge should
                    # correspond to an absent or an abstained vote
                    self.logger.warning(u"no group found for charge vote %s (vote date: %s)" % (cv,votation.sitting.date))

                # continue in any case
                continue

            # get or create group votation
            gv, created = GroupVote.objects.get_or_create(
                votation=votation, group=g,
                defaults={'vote':GroupVote.VOTES.noncomputable}
            )

            if v == ChargeVote.VOTES.yes:
                gv.n_yes += 1
                gv.n_presents += 1
            elif v == ChargeVote.VOTES.no:
                gv.n_no += 1
                gv.n_presents += 1
            elif v == ChargeVote.VOTES.abstained:
                gv.n_abst += 1
                gv.n_presents += 1
            elif v == ChargeVote.VOTES.secret:
                gv.n_presents += 1
            elif v == ChargeVote.VOTES.canceled:
                gv.n_presents += 1
            elif v == ChargeVote.VOTES.pres:
                gv.n_presents += 1
            elif v == ChargeVote.VOTES.absent:
                gv.n_absents += 1
            else:
                pass

            gv.save()

        for gv in votation.group_votes:
            # compute group vote and n of rebels
            if gv.n_yes > gv.n_no and gv.n_yes > gv.n_abst:
                gv.vote = GroupVote.VOTES.yes
                gv.n_rebels = gv.n_no + gv.n_abst

            if gv.n_no > gv.n_yes and gv.n_no > gv.n_abst:
                gv.vote = GroupVote.VOTES.no
                gv.n_rebels = gv.n_abst + gv.n_yes

            if gv.n_abst > gv.n_yes and gv.n_abst > gv.n_no:
                gv.vote = GroupVote.VOTES.abstained
                gv.n_rebels = gv.n_no + gv.n_yes

            # save updates
            gv.save()


    def write_vote(self, vote, db_ballot=None):
        raise Exception("Not implemented")

    def write(self):
        self.setup()

        for sitting in self.sittings:
            try:
                self._write_sitting(sitting)
            except Exception, e:
                import traceback
                self.logger.warning("Error saving sitting. Skip. Detail: %s" % (e, ))
                self.logger.debug("Stacktrace for previous exception: %s" % (traceback.format_exc(), ))

    @transaction.commit_on_success
    def _write_sitting(self, sitting):
        assert isinstance(sitting, SittingItem)
        
        self.logger.info("Processing %s in Mdb" % sitting)
#        self.logger.info("Sitting site code: %s" % sitting.site)
        inst = Institution.objects.get(name=self.conf.XML_TO_OM_INST[sitting.site])

        if not self.dry_run:
            s, sitting_created = OMSitting.objects.get_or_create(
                idnum=sitting._id,
                date=sitting.date,
                defaults={
                    'number':      sitting.sitting_n,
                    'call':        sitting.call,
                    'institution': inst,
                    }
            )
            if sitting_created:
                self.logger.info("%s created in DB" % s)
            else:
                self.logger.debug("%s found in DB" % s)

        for ballot in sitting.ballots:
            assert isinstance(ballot, Ballot)
            
#            self.logger.info("read ballot timestamp: %s" % (ballot.time,))
            ballot_date = ballot.time.date()

            self.logger.info("Processing %s in Mdb" % ballot)
        
            if not sitting_created and sitting.date != ballot_date:
                #raise Exception("Existing sitting number %s, date %s but ballot date is %s" % (sitting.seq_n, sitting.date, ballot_date))
                self.logger.warning("Existing sitting number %s, date %s but ballot date is %s. Proceed with caution ..." % (sitting.seq_n, sitting.date, ballot_date))

            if self.dry_run:
                return
            else:
                # get or create the ballot in the DB
                b, created = OMBallot.objects.get_or_create(
                    idnum=ballot.seq_n,
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
                        'datetime': ballot.time,
                    }
                )

                if created:
                    self.logger.debug("%s created in DB..." % b)
                else:
                    self.logger.debug("%s found in DB, %s votes to import" % (b, len(ballot.votes)))
                    if b.chargevote_set.count():
                        self.logger.info("votation %s: %s votes already present, skip import" \
                            % (b, b.chargevote_set.count()))
                        continue

            for vote in ballot.votes:
                assert isinstance(vote, Vote)
                #self.logger.debug("Processing %s in Mdb" % vote)
                self.write_vote(vote, db_ballot=b)

            # since absences are not explicitly set
            # they must be computed
            self.compute_absences(b)

            try:
                assert isinstance(b, OMBallot)
                b.verify_integrity()
            except Exception, e:
                self.logger.warning("Imported ballot %s (sitting: %s) does not pass integrity check: %s" % (b, b.sitting, e, ))

            # compute and cache group votes into GroupVote
            self.logger.info("Compute group vote of %s (date:%s)" % (b,b.sitting.date))
            self.compute_group_votes(b)

            # compute rebels caches, only if the sitting is not a Committee (no rebellions in committees)
            if b.sitting.institution.institution_type != Institution.COMMITTEE:
                self.update_rebel_caches(b)

            b.update_presence_caches()


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
