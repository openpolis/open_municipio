from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.utils import simplejson as json
import re
from open_municipio.acts.models import Act
from open_municipio.data_import.lib import DataSource, BaseReader, BaseWriter, JSONWriter, XMLWriter, valid_XML_char_ordinal
# import OM-XML language tags
from open_municipio.data_import.om_xml import *
# import models used in DBVotationWriter
from open_municipio.people.models import Institution
from open_municipio.votations.models import Sitting as DBSitting, GroupVote
from open_municipio.votations.models import Votation as DBBallot
from open_municipio.votations.models import ChargeVote


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
        self.logger.info("All sittings: %s" % all_sittings)

        for sitting in all_sittings:
            try:
                sitting.ballots = data_source.get_ballots(sitting)
                self.sittings.append(sitting)
            except Exception, e:
                self.logger.warning("Sitting %s has been skipped because of the following error: %s" % (sitting, e))

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

        # reset: remove all GroupVotes for this votation,
        # so that group votes are never counted more than once
        votation.group_votes.delete()

        for cv in votation.charge_votes:
            g = cv.charge_group_at_vote_date
            v = cv.vote

            if g is None:
                self.logger.warning(u"no group found for charge vote %s (vote date: %s)" % (cv,votation.sitting.date))
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
            self.logger.info("processing %s in Mdb" % sitting)
            self.logger.info("Sitting site code: %s" % sitting.site)
            inst = Institution.objects.get(name=self.conf.XML_TO_OM_INST[sitting.site])

            if not self.dry_run:
                s, sitting_created = DBSitting.objects.get_or_create(
                    idnum=sitting._id,
                    defaults={
                        'number':      sitting.seq_n,
                        'date':        sitting.date,
                        'call':        sitting.call,
                        'institution': inst,
                        }
                )
                if sitting_created:
                    self.logger.info("%s created in DB" % s)
                else:
                    self.logger.debug("%s found in DB" % s)

            for ballot in sitting.ballots:
                self.logger.info("read ballot timestamp: %s" % (ballot.time,))
                ballot_date = ballot.time.date()

                self.logger.info("processing %s in Mdb" % ballot)
            
                if not sitting_created and sitting.date != ballot_date:
                    raise Exception("Existing sitting number %s, date %s but ballot date is %s" % (sitting.seq_n, sitting.date, ballot_date))

                if not self.dry_run:

                    # get or create the ballot in the DB
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

                    # try to link to an act
#                    self.logger.debug("act_descr: %s" % b.act_descr.strip())
#                    m = re.match(r"(.+?)-(.+)", b.act_descr.strip())
#                    if m:
#                        try:
#                            act_idnum = str(m.group(1))
#                            self.logger.debug("act_idnum: %s" % act_idnum)
#                            linked_act = Act.objects.get(idnum=act_idnum)
#                            if isinstance(linked_act, Act):
#                                try:
#                                    b.act = linked_act.downcast()
#                                    b.save()
#                                    self.logger.info("act was linked: %s" % b.act)
#                                except ObjectDoesNotExist:
#                                    self.logger.info("act was not linked")
#
#                            else:
#                                self.logger.warning("act of type %s not expected. expected type Act" % linked_act.__class__.__name__)
#
#                        except ObjectDoesNotExist:
#                            self.logger.warning("act %s not present in OM" % act_idnum)
#                        except Exception as e:
#                            self.logger.warning("unexpected error looking for act %s in OM: %s" % (act_idnum, e))
#
                    if created:
                        self.logger.debug("%s created in DB" % b)
                    else:
                        self.logger.debug("%s found in DB" % b)


                if self.dry_run:
                    continue

                for vote in ballot.votes:
                    self.logger.debug("processing %s in Mdb" % vote)
                    self.write_vote(vote, db_ballot=b)


                # since absences are not explicitly set
                # they must be computed
                self.compute_absences(b)


                # TODO:
                # remove Votation and skip this votation if
                # sums are not verified
                #
                # if not b.verify_sums():
                #   b.delete()
                #   continue

                # compute and cache group votes into GroupVote
                self.logger.info("Compute group vote of %s (date:%s)" % (b,b.sitting.date))
                self.compute_group_votes(b)

                # compute rebels caches, only if the sitting is not a Committee (no rebellions in committees)
                if b.sitting.institution.institution_type != Institution.COMMITTEE:
                    self.update_rebel_caches(b)

                b.update_presence_caches()

                self.logger.info("caches for this votation updated.\n")


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
