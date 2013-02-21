import logging

from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel
from django.utils.translation import ugettext_lazy as _

from open_municipio.acts.models import Document
from open_municipio.people.models import Charge, InstitutionCharge, CompanyCharge,\
    AdministrationCharge, GroupCharge, Person
from open_municipio.events.models import EventAct

from open_municipio.taxonomy.models import Category

class Speech(TimeStampedModel):
    text = models.TextField(blank=True)
    speaker = models.ForeignKey(Person) # do we need a Speaker class?
    event_act = models.ForeignKey(EventAct)
    # whether this speech is a "key" one
    is_key = models.BooleanField(default=False)
    category_set = models.ManyToManyField(Category, verbose_name=_('categories'),
        blank=True, null=True)
    title = models.CharField(max_length=255)
    begin_time = models.TimeField(_("Begin time"), blank=True, null=True, help_text=_("The time when the speech began"))

    def __unicode__(self):
        return "%s - %s on '%s' (%s)" % (self.event_act.event.date, self.title, self.event_act.act.title, self.speaker)

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
    title = models.CharField(max_length=255)
    speech = models.ForeignKey(Speech, related_name='speechattachment_set')

    def __unicode__(self):
        return "%s [%s]" % (self.title, self.speech)
