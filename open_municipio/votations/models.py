from django.db import models
from django.utils.translation import ugettext_lazy as _

from model_utils import Choices
from model_utils.models import TimeStampedModel

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
    
    # activation of the ``is_linked_filter``
    # add ``act`` to the ``list_filter`` list in ``admin.py``
    # to filter votations based on the existence of a related act
    act.is_linked_filter = True
    
    class Meta:
        verbose_name = _('votation')
        verbose_name_plural = _('votations')
        
    @property
    def group_votes(self):
        return self.group_vote_set.all()
    
    @property
    def charge_votes(self):
        return self.charge_vote_set.all()

    @property
    def transitions(self):
        return self.transition_set.all()

    @property
    def is_linked(self):
        if self.act is None:
            return False
        else:
            return True

    @models.permalink
    def get_absolute_url(self):
        return 'om_votation_detail', [str(self.pk)]
        
    def __unicode__(self):
        return u'votation %s' % self.idnum


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
