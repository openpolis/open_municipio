from django.db import models
from django.db.models.aggregates import Count
from django.utils.translation import ugettext_lazy as _

from model_utils import Choices
from model_utils.models import TimeStampedModel
from model_utils.managers import QueryManager
import sys

from open_municipio.people.models import Group, InstitutionCharge, Sitting 
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
    n_presents = models.IntegerField(blank=True, null=True)
    n_yes = models.IntegerField(blank=True, null=True)
    n_no = models.IntegerField(blank=True, null=True)
    n_abst = models.IntegerField(blank=True, null=True)
    n_maj = models.IntegerField(blank=True, null=True)
    outcome = models.IntegerField(choices=OUTCOMES, blank=True, null=True)
    is_key = models.BooleanField(default=False, help_text=_("Specify whether this is a key votation"))
    n_rebels = models.IntegerField(default= 0)
    
    # use this manager to retrieve only key votations
    key = QueryManager(is_key=True).order_by('-sitting__date')

    # default manager must be explicitly defined, when
    # at least another manager is present
    objects = models.Manager()
    
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

    def compute_group_votes(self):
        """
        once all charges' votes have been stored, the aggregated votations
        of the groups are stored in GroupVote.

        A GroupVote is the same as the majority of the group.
        Whenever there is no clear majority (50%/50%), then a
        Not Available vote can be assigned to the Group.
        """

        # the computation is done only if ChargeVote is populated,
        # for this votation
        if ChargeVote.objects.filter(votation__id=self.id).count() > 0:

            for g in Group.objects.all():
                # extract the 2 most voted votes for this group,
                # in this votation
                most_voted = ChargeVote.objects.filter(votation__id=self.id,
                                                       charge__groupcharge__group=g,
                                                       charge__groupcharge__end_date__isnull=True).\
                                                 values('vote').\
                                                 annotate(Count('vote')).\
                                                 order_by('-vote__count')[0:2]

                # if equal, then set to not available
                if (len(most_voted) == 1 or
                    most_voted[0]['vote__count'] > most_voted[1]['vote__count']):
                    vote = most_voted[0]['vote']
                else:
                    vote = GroupVote.NON_COMPUTABLE

                # get or create group votation
                gv, created = GroupVote.objects.get_or_create(votation=self, group=g, defaults={'vote':vote})





    def compute_rebel_votes(self):
        """
        A ChargeVote must be marked as ``rebel`` when her vote is different
        from that of her group.

        The ``rebel`` field can be assigned only if the counselor is present and
         if her group's vote is clearly defined (i.e., it is not *Not Avaliable*)

        This is only valid for council votations.

        After a rebel vote has been set, the following *caches* should be updated:

        * Votation.n_rebels - counts the total number of rebels for that votation
        * InstitutionCharge.n_rebel_votations - counts the total number of votations
          where charge's vote was *rebel*
        """
        for v in self.charge_votes:
            charge_vote = v.vote
            group_vote = v.charge.council_group.groupvote_set.get(votation=self).vote
            if charge_vote != group_vote:
                v.rebel = True
                v.save()

                # upgrade charge cache
                v.charge.update_n_rebel_votations()

        self.update_n_rebels()

    def update_n_rebels(self):
        """
        Re-compute the number of rebel votes for this votation and update the n_rebels counter
        """
        self.n_rebels = self.chargevote_set.filter(rebel=True).count()
        self.save()


class GroupVote(TimeStampedModel):
    """
    WRITEME
    """
    NO = 0
    YES = 1
    ABSTAINED = 2
    NON_COMPUTABLE = 3
    VOTES = Choices(
      (YES, _('Yes')),    
      (NO, _('No')),
      (ABSTAINED, _('Abstained')),
      (NON_COMPUTABLE, _('Non computable')),
    )
    
    votation = models.ForeignKey(Votation)
    vote = models.IntegerField(choices=VOTES)
    group = models.ForeignKey(Group)
    
    class Meta:
        db_table = u'votations_group_vote'    
        verbose_name = _('group vote')
        verbose_name_plural = _('group votes')


class ChargeVote(TimeStampedModel):
    """
    WRITEME
    """  
    NO = 0
    YES = 1
    ABSTAINED = 2
    MISSION = 3
    ABSENT = 4
    INVALID = 5
    PRES = 6
    REQUIRES = 7
    CANCELED = 8
    SECRET = 9
    VOTES = Choices(
    (YES, _('Yes')),    
    (NO, _('No')),
    (ABSTAINED, _('Abstained')),
    (MISSION, _('Is on mission')),
    (ABSENT, _('Is absent')),
    (INVALID, _('Participates to an invalid votation')),
    (PRES, _('President during votation')),
    (REQUIRES, _('Requires votation, but does not vote')),
    (CANCELED, _('Canceled votation')),
    (SECRET, _('Secret votation')),
    )
    
    votation = models.ForeignKey(Votation)
    vote = models.IntegerField(choices=VOTES)
    charge = models.ForeignKey(InstitutionCharge)
    rebel = models.BooleanField(default=False)
    
    class Meta:
        db_table = u'votations_charge_vote'    
        verbose_name = _('charge vote')
        verbose_name_plural = _('charge votes')
