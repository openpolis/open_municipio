import logging

from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel
from django.utils.translation import ugettext_lazy as _

from open_municipio.acts.models import Document
from open_municipio.people.models import Charge, InstitutionCharge, CompanyCharge,\
    AdministrationCharge, GroupCharge, Person
#from open_municipio.events.models import EventAct
from open_municipio.acts.models import Act


from open_municipio.taxonomy.models import Category

class Speech(TimeStampedModel):
    text = models.TextField(blank=True)
    speaker = models.ForeignKey(Person, verbose_name=_('speaker')) # do we need a Speaker class?
    act = models.ForeignKey(Act, verbose_name=_('act'))
    is_key = models.BooleanField(default=False, help_text=_("Specify whether this speech should be featured"))
    category_set = models.ManyToManyField(Category, verbose_name=_('categories'),
        blank=True, null=True)
    title = models.CharField(max_length=255,verbose_name=_('title'))
    begin_time = models.TimeField(verbose_name=_("Begin time"), blank=True, null=True, help_text=_("The time when the speech begin"))

    def __unicode__(self):
        return "%s on '%s' (%s)" % (self.title, self.act.title, self.speaker)


    @property
    def attachments(self):
        """
        A queryset of speech-attachments linked to this speech.
        """
        return self.speechattachment_set.all()

    class Meta:
        verbose_name = _('speech')
        verbose_name_plural = _('speeches')

class SpeechAttachment(Document):
    title = models.CharField(max_length=255, verbose_name=_('title'))
    speech = models.ForeignKey(Speech, related_name='speechattachment_set',verbose_name=_('speech'))

    def __unicode__(self):
        return "%s [%s]" % (self.title, self.speech)

    class Meta:
        verbose_name = _('speech attachment')
        verbose_name_plural = _('speech attachments')
