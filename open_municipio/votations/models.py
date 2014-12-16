import locale
import datetime
import re

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify


from model_utils import Choices
from model_utils.models import TimeStampedModel
from model_utils.managers import QueryManager

from open_municipio.people.models import Group, InstitutionCharge, Sitting, Institution
from open_municipio.acts.models import Act


class Votation(models.Model):
    """
    WRITEME
    """
    OUTCOMES = Choices(
        (0, 'No Esito'),
        (1, 'Approvato'),
        (2, 'Respinto'),
        (3, 'SI Numero Legale'),
        (4, 'NO Numero Legale'),
        (5, 'Annullata'),
    )

    idnum = models.CharField(blank=True, max_length=64)
    sitting = models.ForeignKey(Sitting, blank=False, null=False)
    act = models.ForeignKey(Act, null=True)
    
    # this field is used to keep the textual description of the related act
    # as expressed in the voting system
    act_descr = models.CharField(blank=True, max_length=255)
    
    group_set = models.ManyToManyField(Group, through='GroupVote')
    charge_set = models.ManyToManyField(InstitutionCharge, through='ChargeVote')
    n_legal = models.IntegerField(default=0)
    n_presents = models.IntegerField(default=0)
    n_partecipants = models.IntegerField(default=0)
    n_absents = models.IntegerField(default=0)
    n_yes = models.IntegerField(default=0)
    n_no = models.IntegerField(default=0)
    n_abst = models.IntegerField(default=0)
    n_maj = models.IntegerField(default=0)
    outcome = models.IntegerField(choices=OUTCOMES, blank=True, null=True)
    is_key = models.BooleanField(default=False, help_text=_("Specify whether this is a key votation"))    
    n_rebels = models.IntegerField(default= 0)
    slug = models.SlugField(max_length=500, blank=True, null=True)

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

    @property
    def is_key_yesno(self):
        if self.is_key:
            return _('yes')
        else:
            return _('no')

    def save(self, *args, **kwargs):
        """
        This method takes care of setting a default slug for Votations
        that are linked to a Sitting. 

        This transparently helps the slug field for most of the "normal"
        use cases of Votation.
        """
        if not self.slug:
            self.slug = self.get_default_slug()

        super(Votation, self).save(*args, **kwargs)

    @property
    def date(self):
        return self.sitting.date

    def get_default_slug(self):
        """
        This method will be used for assigning a default slug to a
        Votation that does not have one.
        """

        if self.sitting and self.idnum:
            cleaned_idnum = re.sub(r'[^\w\d]+', '-', self.idnum)
            slug = slugify("%s-%s" % (self.sitting.date.isoformat(), 
                                        cleaned_idnum))
            return slug[:100]
        else:
            raise ValueError("In order to compute the default slug, the Votation should be linked to a Sitting")
                
                

    class Meta:
        verbose_name = _('votation')
        verbose_name_plural = _('votations')

        unique_together = (('slug',), ('sitting','idnum',))
    
    def __unicode__(self):
        
        return _('Votation %(idnum)s') % { "idnum":self.idnum, }

    @models.permalink
    def get_absolute_url(self):
        """
        Introduce url based on slugs. To keen retro-compatibility during 
        introduction of slugs, it also allows to view the old url using pk.
        """

        if getattr(self, "slug", None) and self.slug:
            return ("om_votation_detail", (), {'slug': self.slug })
        else:
            return ("om_votation_detail", (), {'pk': self.pk })
           


    
    @property
    def group_votes(self):
        return self.groupvote_set.all()
    
    @property
    def charge_votes(self):
        return self.chargevote_set.all()
    
    @property
    def charge_rebel_votes(self):
        return self.chargevote_set.filter(is_rebel=True)

    @property
    def transitions(self):
        return self.transition_set.all()

    @property
    def ref_act(self):
        if self.act:
            return self.act
        elif self.transitions.count() > 0:
            return self.transitions[0].act
        else:
            return None

    @property
    def is_linked(self):
        return self.ref_act is not None

    @property
    def is_secret(self):
        for vote in self.charge_votes:
            return vote.vote == ChargeVote.VOTES.secret

    def update_presence_caches(self):
        """
        update presence caches for each voting charge of this votation
        """
        for vc in self.charge_votes:
            vc.charge.update_presence_cache()
            
    def verify_integrity(self):
        """
        Verify the integrity of the ballot structure. In particular checks that 
        related self.votes are consistent with the votes counted in the self.n_*
        fields. If an error is detected, raise an exception explaining the problem
        """
        errors = []
        
        # check legal number is greater than 0
        if self.n_legal < 0:
            errors.append("The legal number should always be positive. Passed: %s" % self.n_legal)

        # count the number of presents is consistent with yes + no + abstained

        n_sum = self.n_yes + self.n_no + self.n_abst
        if n_sum > self.n_presents:
            errors.append("The number of presents (%s) is smaller than the sum of yes (%s), no (%s) and abstained (%s): %s. Additional info: absents = %s, rebels = %s" % (self.n_presents, self.n_yes, self.n_no, self.n_abst, n_sum, self.n_absents, self.n_rebels))
        
        num_charge_votes = self.charge_votes.count()
        if num_charge_votes < self.n_presents:
            errors.append("The related votes (%s) are less that the reported number of presents (%s)" %
                            (num_charge_votes, self.n_presents, ))
        
        if num_charge_votes < n_sum:
            errors.append("The number of related votes (%s) is less than the yes, no and abst votes (%s)" %
                            (num_charge_votes, n_sum, ))
      
        # check the number of presents is greater than the legal number

        if self.n_presents < self.n_legal:
            errors.append("Number of presents (%s) should not be less than legal number (%s)" % (self.n_presents, self.n_legal))
  
        if len(errors) > 0:
            raise Exception(",".join(errors))



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

    def __unicode__(self):
        return u"%s - %s - %s" % (self.votation, self.group.acronym, self.get_vote_display())


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
    
    votation = models.ForeignKey(Votation, verbose_name=_('votation'))
    vote = models.CharField(choices=VOTES, max_length=12, verbose_name=_('vote'))
    charge = models.ForeignKey(InstitutionCharge, verbose_name=_('charge'))
    is_rebel = models.BooleanField(default=False, verbose_name=_('is rebel'))

    @property
    def original_charge(self):
        """
        Charge in committees are connected to an original Counselor charge.
        Using original_charge assures you always refer to the counselor InstitutionCharge
        """
        if self.charge.original_charge is not None:
            return self.charge.original_charge
        else:
            return self.charge

    @property
    def charge_group_at_vote_date(self):
        return self.original_charge.person.get_current_group(moment=self.votation.sitting.date.strftime('%Y-%m-%d'))
    
    class Meta:
        db_table = u'votations_charge_vote'    
        verbose_name = _('charge vote')
        verbose_name_plural = _('charge votes')

    def __unicode__(self):
        return u"%s - %s - %s" % (self.votation, self.original_charge.person, self.get_vote_display())


