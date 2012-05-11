from django.db import models
from django.db.models.aggregates import Count
from django.utils.translation import ugettext_lazy as _

from model_utils import Choices
from model_utils.models import TimeStampedModel
from model_utils.managers import QueryManager
import sys

from open_municipio.people.models import Group, InstitutionCharge, Sitting, Institution
from open_municipio.acts.models import Act


class Votation(models.Model):
    """
    WRITEME
    """
    REJECTED = 0
    PASSED = 1
    OUTCOMES = Choices(
      (PASSED, _('Passed')),    
      (REJECTED, _('Rejected')),
    )
    
    idnum = models.CharField(blank=True, max_length=64)
    sitting = models.ForeignKey(Sitting, null=True)
    act = models.ForeignKey(Act, null=True)
    
    # this field is used to keep the textual description of the related act
    # as expressed in the voting system
    act_descr = models.CharField(blank=True, max_length=255)
    
    group_set = models.ManyToManyField(Group, through='GroupVote')
    charge_set = models.ManyToManyField(InstitutionCharge, through='ChargeVote')
    n_legal = models.IntegerField(blank=True, null=True)
    n_presents = models.IntegerField(default=0)
    n_absents = models.IntegerField(default=0)
    n_yes = models.IntegerField(default=0)
    n_no = models.IntegerField(default=0)
    n_abst = models.IntegerField(default=0)
    n_maj = models.IntegerField(blank=True, null=True)
    outcome = models.IntegerField(choices=OUTCOMES, blank=True, null=True)
    is_key = models.BooleanField(default=False, help_text=_("Specify whether this is a key votation"))    
    n_rebels = models.IntegerField(default= 0)

    # default manager must be explicitly defined, when
    # at least another manager is present
    objects = models.Manager()

    # use this manager to retrieve only key votations
    key = QueryManager(is_key=True).order_by('-sitting__date')

    # use this manager to retrieve only linked acts
    is_linked_to_act = QueryManager(act__isnull=False)

    # activation of the ``is_linked_filter``
    # add ``act`` to the ``list_filter`` list in ``admin.py``
    # to filter votations based on the existence of a related act
    act.is_linked_filter = True
    
    class Meta:
        verbose_name = _('votation')
        verbose_name_plural = _('votations')
    
    def __unicode__(self):
        return u'votation %s' % self.idnum

    @models.permalink
    def get_absolute_url(self):
        return 'om_votation_detail', [str(self.pk)]
    
    @property
    def group_votes(self):
        return self.groupvote_set.all()
    
    @property
    def charge_votes(self):
        return self.chargevote_set.all()

    @property
    def transitions(self):
        return self.transition_set.all()

    @property
    def is_linked(self):
        if self.act is None:
            return False
        else:
            return True

    def update_caches(self):
        """
        Computes and update caches for this votation.

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
        * InstitutionCharge.n_absent_votations - total number of votations
                                                 where charge was not present
        * InstitutionCharge.n_present_votations - total number of votations
                                                  where charge was present
        * InstitutionCharge.n_rebel_votations - total number of votations
                                                where charge's vote was *rebel*

        An absence MUST be explicitly set as a vote type (ChargeVote.ABSENT)
        """

        # computes and caches group votes
        self.compute_group_votes()

        # compute rebel votes and presence caches
        for vc in self.charge_votes:
            charge_vote = vc.vote
            group_vote = vc.charge.current_groupcharge.group.groupvote_set.get(votation=self).vote
            if charge_vote != group_vote:
                vc.is_rebel = True
                vc.save()

            # compute new cache for the single charge
            vc.charge.compute_rebellion_cache()
            vc.charge.compute_presence_cache()

        self.n_rebels = self.chargevote_set.filter(is_rebel=True).count()
        self.save()



    def compute_group_votes(self):
        """
        once all charges' votes have been stored, the aggregated votations
        of the groups are stored in GroupVote.vote

        A GroupVote is the same as the majority of the group.
        Whenever there is no clear majority (50%/50%), then a
        Not Available vote can be assigned to the Group.

        Other cached values are stored in GroupVote, as well:
        * n_presents
        * n_yes
        * n_no
        * n_abst
        * n_rebels
        * n_absents

        the number of total group members is len(g.counselors())
        and it should be cached somewhere,
        then n_absents = n_group_members - n_presents

        """

        # the computation is done only if ChargeVote is populated,
        # for this votation
        if ChargeVote.objects.filter(votation__id=self.id).count() > 0:

            for g in Group.objects.all():
                # compute votation details for the group
                # differentiate between council and committee queries
                annotated_votes = ChargeVote.objects.filter(votation__id=self.id,
                                                            charge__groupcharge__group=g,
                                                            charge__groupcharge__end_date__isnull=True).\
                values('vote').\
                annotate(Count('vote'))
                if not len(annotated_votes):
                    continue

                # extract the 2 most voted votes for this group,
                # in this votation
                most_voted = annotated_votes.order_by('-vote__count')[0:2]


                # if equal, then set to not available
                if (len(most_voted) == 1 or
                    most_voted[0]['vote__count'] > most_voted[1]['vote__count']):
                    vote = most_voted[0]['vote']
                else:
                    vote = GroupVote.VOTES.noncomputable

                # get or create group votation
                gv, created = GroupVote.objects.get_or_create(votation=self, group=g, defaults={'vote':vote})

                # update other cached values
                votes_cnt = 0
                n_rebels = 0
                for v in annotated_votes:
                    if v['vote'] == ChargeVote.VOTES.no:
                        gv.n_no = v['vote__count']
                    elif v['vote'] == ChargeVote.VOTES.yes:
                        gv.n_yes = v['vote__count']
                    elif v['vote'] == ChargeVote.VOTES.abstained:
                        gv.n_abst = v['vote__count']
                    else:
                        pass
                    votes_cnt += v['vote__count']

                    # compute n_rebels
                    if v['vote'] == ChargeVote.VOTES.yes or\
                       v['vote'] == ChargeVote.VOTES.no or\
                       v['vote'] == ChargeVote.VOTES.abstained:
                        if vote != GroupVote.VOTES.noncomputable and \
                           v['vote'] > 0 and v['vote'] != vote:
                            n_rebels += v['vote__count']

                # presences = n. of total votes
                # presidents, mission, and ther are counted
                gv.n_presents = votes_cnt

                # count absences
                gv.n_absents = len(g.institution_charges) - gv.n_presents

                # n_rebels in group
                gv.n_rebels = n_rebels

                # save updates
                gv.save()


class GroupVote(TimeStampedModel):
    """
    WRITEME
    """
    VOTES = Choices(
      ('YES', 'yes', _('Yes')),
      ('NO', 'no', _('No')),
      ('ABSTAINED', 'abstained', _('Abstained')),
      ('NON_COMPUTABLE', 'noncomputable', _('Non computable')),
    )
    
    votation = models.ForeignKey(Votation)
    vote = models.CharField(choices=VOTES, max_length=16)
    group = models.ForeignKey(Group)

    # cache fields
    n_presents = models.IntegerField(default=0)
    n_yes = models.IntegerField(default=0)
    n_no = models.IntegerField(default=0)
    n_abst = models.IntegerField(default=0)
    n_rebels = models.IntegerField(default=0)
    n_absents = models.IntegerField(default=0)

    class Meta:
        db_table = u'votations_group_vote'    
        verbose_name = _('group vote')
        verbose_name_plural = _('group votes')


class ChargeVote(TimeStampedModel):
    """
    WRITEME
    """  
    VOTES = Choices(
        ('YES', 'yes', _('Yes')),
        ('NO', 'no', _('No')),
        ('ABSTAINED', 'abstained', _('Abstained')),
        ('CANCELED', 'canceled', _('Vote was canceled')),
        ('PRES', 'pres', _('Present but not voting')),
        ('SECRET', 'secret', _('Secret votation')),
        ('ABSENT', 'absent', _('Is absent')),
        ('UNTRACKED', 'untracked', _('Vote was not tracked')),  # nothing can be said about presence
    )
    
    votation = models.ForeignKey(Votation)
    vote = models.CharField(choices=VOTES, max_length=12)
    charge = models.ForeignKey(InstitutionCharge)
    is_rebel = models.BooleanField(default=False)
    
    class Meta:
        db_table = u'votations_charge_vote'    
        verbose_name = _('charge vote')
        verbose_name_plural = _('charge votes')
