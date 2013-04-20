import logging

from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist

from open_municipio.acts.models import Document
from open_municipio.people.models import Charge, InstitutionCharge,CompanyCharge,\
    AdministrationCharge, GroupCharge, Person, Institution
from open_municipio.acts.models import Act


from open_municipio.taxonomy.models import Category

class Speech(TimeStampedModel):
    text = models.TextField(blank=True)
    speaker = models.ForeignKey(Person, verbose_name=_('speaker'), related_name='speeches_set') # do we need a Speaker class?
    act = models.ForeignKey(Act, verbose_name=_('act'))
    is_key = models.BooleanField(default=False, help_text=_("Specify whether this speech should be featured"))
    category_set = models.ManyToManyField(Category, verbose_name=_('categories'),
        blank=True, null=True)
    title = models.CharField(max_length=255,verbose_name=_('title'))
    date = models.DateField(blank=True, null=True)
    begin_time = models.TimeField(verbose_name=_("Begin time"), blank=True, null=True, help_text=_("The time when the speech begin"))

    def __unicode__(self):
        return "%s on '%s' (%s)" % (self.title, self.act.title, self.speaker)

    @models.permalink
    def get_absolute_url(self):
        return ('om_speech_detail', (), {'pk' : str(self.pk)})

    @property
    def speaker_counselor(self):
        politician = None
        try:
            politician = InstitutionCharge.objects.get(person=self.speaker,institution__institution_type=Institution.COUNCIL)
        except ObjectDoesNotExist:
            pass
    
        print "counselor found: %s" % politician

        return politician

    @property
    def attachments(self):
        """
        A queryset of speech-attachments linked to this speech.
        """
        return self.speechattachment_set.all()

    @property
    def is_public(self):
        return self.act == None or self.act.status_is_final

    @property
    def act_title_cut(self):
        max_len = 30
        title_cut = self.act.title
        length = len(title_cut)
        if length > (max_len * 2):
            title_cut = "%s...%s" % (title_cut[0:max_len], \
                title_cut[length-max_len:length])
            
        return title_cut

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
