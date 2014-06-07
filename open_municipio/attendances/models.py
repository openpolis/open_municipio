import locale
import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from model_utils import Choices
from model_utils.models import TimeStampedModel
from model_utils.managers import QueryManager

from open_municipio.people.models import Group, InstitutionCharge, Sitting, Institution
from open_municipio.acts.models import Act


class Attendance(models.Model):

    OUTCOMES = Choices(
        (0, 'No outcome', _('No outcome')),
        (1, 'Yes legal number', _('Yes legal number')),
        (2, 'No legal number', _('No legal number')),
        (3, 'Rejected', _('Rejected')),
    )


    idnum = models.CharField(blank=True, max_length=64, null=True, verbose_name=_('idact'))
    sitting = models.ForeignKey(Sitting, null=True, verbose_name=_('sitting'))
    act = models.ForeignKey(Act, null=True, verbose_name=_('act'))
    
    # this field is used to keep the textual description of the related act
    # as expressed in the attendance system
    act_descr = models.CharField(blank=True, max_length=255, verbose_name=_('act description'))
    
    charge_set = models.ManyToManyField(InstitutionCharge, through='ChargeAttendance', verbose_name=_('charges'))
    n_legal = models.IntegerField(default=0, verbose_name=_('legal number'))
    n_presents = models.IntegerField(default=0, verbose_name=_('num. presents'))
    n_absents = models.IntegerField(default=0, verbose_name=_('num. absents'))
    outcome = models.IntegerField(choices=OUTCOMES, blank=True, null=True, verbose_name=_('outcome'))
    is_key = models.BooleanField(default=False, help_text=_("Specify whether this is a key attendance"), verbose_name=_('is key attendance'))    

    # default manager must be explicitly defined, when
    # at least another manager is present
    objects = models.Manager()

    # use this manager to retrieve only key attendances
    key = QueryManager(is_key=True).order_by('-sitting__date')

    # use this manager to retrieve only linked acts
    is_linked_to_act = QueryManager(act__isnull=False)

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
        return (self.ref_act is not None)

    class Meta:
        verbose_name = _("attendance")
        verbose_name_plural = _("attendances")

    def __unicode__(self):
        idnum = ''
        if self.idnum:
            idnum = ' %(idnum)s' % { 'idnum':self.idnum, }
        date = ''
        if self.sitting:
            date = _(' of %(date)s') % { 'date':self.sitting.date, }
        return _('Attendance%(idnum)s%(date)s') % { 'idnum':idnum, 'date':date }


class ChargeAttendance(TimeStampedModel):
    """
    This model expresses whether a charge is present or not during the sitting
    linked to the Attendance instance.
    """  
    VALUES = Choices(
        ('PRES', 'pres', _('Present')),
        ('ABSENT', 'absent', _('Is absent')),
        ('MISSION', 'mission', _('On a mission')),
    )
    
    attendance = models.ForeignKey(Attendance, verbose_name=_('attendance'))
    value = models.CharField(choices=VALUES, max_length=12, verbose_name=_('value'))
    charge = models.ForeignKey(InstitutionCharge, verbose_name=_('charge'))

    class Meta:
        verbose_name = _("charge attendance")
        verbose_name_plural = _("charge attendances")
