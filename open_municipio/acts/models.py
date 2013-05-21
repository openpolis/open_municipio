# -*- coding: utf-8 -*-
import logging
from datetime import date
from django.core.exceptions import ObjectDoesNotExist
from south.modelsinspector import add_ignored_fields
from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.template.context import Context
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver

from model_utils import Choices
from model_utils.managers import InheritanceManager, QueryManager
from model_utils.models import TimeStampedModel
from model_utils.fields import StatusField

from open_municipio.newscache.models import News, NewsTargetMixin

from open_municipio.people.models import Institution, InstitutionCharge, Person
from open_municipio.taxonomy.managers import TopicableManager
from open_municipio.monitoring.models import MonitorizedItem, Monitoring


#
# Acts
#

class Act(NewsTargetMixin, MonitorizedItem, TimeStampedModel):
    """
    This is the base class for all the different act types: it contains the common fields for
    deliberations, interrogations, interpellations, motions, agendas and emendations.
  
    it is a ``TimeStampedModel``, so it tracks creation and modification timestamps for each record.

    The ``related_news`` attribute can be used  to fetch news related to a given act.

    Inheritance is done through multi-table inheritance, since browsing the whole set of acts may be useful.
    The default manager is the ``InheritanceManager`` (from package `django-model-utils`_),
    providing the ``select_subclasses()`` method, which allows the retrieval of concrete subclasses' instances, 
    if needed.


    .. _django-model-utils: https://bitbucket.org/carljm/django-model-utils/src

    """
    # added to avoid problems with South migrations
    add_ignored_fields(["^open_municipio\.taxonomy\.managers"])

    idnum = models.CharField(max_length=64, blank=True, help_text=_("A string representing the identification or sequence number for this act, used internally by the municipality's administration."))
    title = models.CharField(_('title'), max_length=1024, blank=True)
    adj_title = models.CharField(_('adjoint title'), max_length=1024, blank=True, help_text=_("An adjoint title, added to further explain an otherwise cryptic title"))
    presentation_date = models.DateField(_('presentation date'), null=True, help_text=_("Date of presentation, as stated in the act"))
    description = models.TextField(_('description'), blank=True)
    text = models.TextField(_('text'), blank=True)
    presenter_set = models.ManyToManyField(InstitutionCharge, blank=True, null=True, through='ActSupport', related_name='presented_act_set', verbose_name=_('presenters'))
    recipient_set = models.ManyToManyField(InstitutionCharge, blank=True, null=True, related_name='received_act_set', verbose_name=_('recipients'))
    emitting_institution = models.ForeignKey(Institution, related_name='emitted_act_set', verbose_name=_('emitting institution'))
    category_set = models.ManyToManyField('taxonomy.Category', verbose_name=_('categories'), blank=True, null=True)
    location_set = models.ManyToManyField('locations.Location', through='locations.TaggedActByLocation', verbose_name=_('locations'), blank=True, null=True)
    status_is_final = models.BooleanField(default=False)
    is_key = models.BooleanField(default=False, help_text=_("Specify whether this act should be featured"))

    objects = InheritanceManager()
    # use this manager to retrieve only key acts
    featured = QueryManager(is_key=True).order_by('-presentation_date') 
    
    tag_set = TopicableManager(through='taxonomy.TaggedAct', blank=True)

    # use this manager to retrieve the QuerySet of ``Monitoring`` instances 
    # having as their ``content_object`` this act
    monitoring_set = generic.GenericRelation(Monitoring, object_id_field='object_pk')

    def __unicode__(self):
        rv = u'%s' % (self.title, )
        if self.idnum:
            rv = u'%s - %s' % (self.idnum, rv)
        if self.adj_title:
            rv = u'%s (%s)' % (rv, self.adj_title)
        return rv

    def downcast(self):
        """
        Returns the "downcasted"[*]_ version of this model instance.
        

        .. [*]: In a multi-table model inheritance scenario, the term "downcasting"
                refers to the process of retrieving the child model instance given the 
                parent model instance.
        """
        # FIXME: this check is redundant, IMO (@seldon)
        # if this method is called from a "concrete" instance
        # the lookup machinery either will return the instance itself
        # or a downcasted version of it (if any), which seems to me 
        # the right behaviour for a ``downcast()`` method.
        if hasattr(self, 'act_ptr'): # method is being called from a subclass' instance
            return self
        cls = self.__class__ # ``self`` is an instance of the parent model
        for r in cls._meta.get_all_related_objects():
            if not issubclass(r.model, cls) or\
               not isinstance(r.field, models.OneToOneField):
                continue
            try:
                return getattr(self, r.get_accessor_name())
            except models.ObjectDoesNotExist:
                continue
    
    @property
    def attachments(self):
        return self.attachment_set.all()

    @property
    def transitions(self):
        return self.transition_set.all()

    @property
    def presenters(self):
        return self.presenter_set.all()

    @property
    def first_presenters(self):
        return self.presenter_set.filter(actsupport__support_date=self.presentation_date)

    @property
    def recipients(self):
        return self.recipient_set.all()
    
    @property
    def first_signers(self):
        # FIXME: resolve asymmetry between this query and that for ``co_signers`` property
        return InstitutionCharge.objects.filter(actsupport__act__id = self.pk,
                                                actsupport__support_type=ActSupport.SUPPORT_TYPE.first_signer)
    @property
    def co_signers(self):
        # FIXME: resolve asymmetry between this query and that for ``first_signers`` property
        return self.presenter_set.filter(actsupport__support_type=ActSupport.SUPPORT_TYPE.co_signer)

    @property
    def emendations(self):
        return self.emendation_set.all()

    @property
    def tags(self):
        # FIXME: cleanup needed, here!
        return list(set([ topic.tag for topic in self.topics if topic.tag is not None ]))

    @property
    def categories(self):
        # FIXME: cleanup needed, here!
        return list( set([ topic.category for topic in self.topics if topic.category is not None]) )

    @property
    def topics(self):
        return self.tag_set.topics()
    
    @property
    def locations(self):
        return self.location_set.all()
    
    @property
    def act_descriptors(self):
        """
        Return the QuerySet of all those users which modified this act's description.
        """
        return self.actdescriptor_set.all()
    
    @property
    def is_key_yesno(self):
        # FIXME: this property should be implemented as a template filter,
        # since it only contains presentational logic
        if self.is_key:
            return _('yes')
        else:
            return _('no')


    def status(self):
        """
        Return the current status for the downcasted version of this act instance.
        
        .. note:: 

            It seems that this method cannot be made into a property,
            since doing that would trigger an ``AttributeError: can't set attribute`` exception 
            during Django initialization. 

        """
        return self.downcast().status
        
    def get_transitions_groups(self):
        """
        Retrieve a list of transitions grouped by status.
        """
        # TODO: review implementation
        groups = {}
        this = self.downcast()
        if not hasattr(this, 'STATUS'):
            return groups
        # initialize all status with an empty list of transitions
        for status in this.STATUS:
            groups[status[0]] = []
        # fill groups with ordered transitions
        for transition in this.transitions.order_by('-transition_date'):
            if groups.has_key(transition.final_status):
                groups.get(transition.final_status).append(transition)
        return groups

    def is_final_status(self, status=None):
        """
        WRITEME
        """
        # TODO: review implementation
        this = self.downcast()
        if status is None:
            status = this.status

        if not hasattr(this, 'FINAL_STATUSES'):
            return False

        for final_status in this.FINAL_STATUSES:
            if status == final_status[0]:
                return True
        return False

    def get_last_transition(self):
        """
        WRITEME
        """
        # TODO: review implementation
        if self.transitions:
            # FIXME: this assume that transitions are ordered by date
            return list(self.transitions)[-1]
        # FIXME: this method returns different kind of objects (list or boolean) 
        # under different conditions: this is not an ideal API!
        # A better approach would be to return ``None`` or raise an exception
        # if no transitions exist for this act
        return False

    def get_absolute_url(self):
        return self.downcast().get_absolute_url()

    def get_type_name(self):
        """
        WRITEME
        """
        if self.downcast():
            return self.downcast()._meta.verbose_name
        else:
            return None

    class Meta:
        verbose_name = _('act')
        verbose_name_plural = _('acts')


class ActSection(models.Model):
    """
    A section (or sub-section) of an act's text content.

    .. note::
    
    Currently, this feature is not being used, but it likely be in future releases

    """
    act = models.ForeignKey(Act, on_delete=models.PROTECT)
    parent_section = models.ForeignKey('self', on_delete=models.PROTECT)  
    title = models.CharField(max_length=1024, blank=True)
    text = models.TextField(blank=True)
  
    def __unicode__(self):
        return u'%s' % self.title

    class Meta:
        db_table = u'acts_act_section'

    @property
    def emendations(self):
        return self.emendation_set.all()


class ActSupport(models.Model):
    """
    A relationship describing which institutional charge(s) 
    signed a given act (a.k.a. "act supporters").
    """
    SUPPORT_TYPE = Choices(
        ('FIRSTSIGNER', 'first_signer', _('first signer')),
        ('COSIGNER', 'co_signer', _('co-signer'))
    )

    charge = models.ForeignKey(InstitutionCharge)
    act = models.ForeignKey(Act)
    support_type = models.CharField(choices=SUPPORT_TYPE, max_length=12)
    support_date = models.DateField(_('support date'), default=None, blank=True, null=True)

    class Meta:
        db_table = u'acts_act_support'


class ActDescriptor(TimeStampedModel):
    """
    A relationship mapping politicians who added or modified an act's description.
    """
    person = models.ForeignKey(Person)
    act = models.ForeignKey(Act)

    class Meta:
        db_table = u'acts_act_descriptor'


class CGDeliberation(Act):
    """
    City Government Deliberation (Delibera di Giunta)
    """
    INITIATIVE_TYPES = Choices(
        ('PRESIDENT', 'president', _('President')),
        ('ASSESSOR', 'assessor', _('City Government Member')),
        ('GOVERNMENT', 'government', _('City Government')),
        ('MAYOR', 'mayor', _('Mayor')),
    )

    FINAL_STATUSES = (
        ('APPROVED', _('approved')),
        ('REJECTED', _('rejected')),
    )

    STATUS = Choices(
        ('PRESENTED', 'presented', _('presented')),
        ('COMMITTEE', 'committee', _('committee')),
        ('COUNCIL', 'council', _('council')),
        ('APPROVED', 'approved', _('approved')),
        ('REJECTED', 'rejected', _('rejected')),
    )

    status = StatusField()
    approval_date = models.DateField(_('approval date'), null=True, blank=True)
    publication_date = models.DateField(_('publication date'), null=True, blank=True)
    final_idnum = models.CharField(max_length=64, blank=True, null=True, help_text=_("Internal identification string for the deliberation, when approved"))
    execution_date = models.DateField(_('execution date'), null=True, blank=True)
    initiative = models.CharField(_('initiative'), max_length=12, choices=INITIATIVE_TYPES)
    approved_text = models.TextField(blank=True)

    class Meta:
        verbose_name = _('city government deliberation')
        verbose_name_plural = _('city government deliberations')

    @property
    def next_events(self):
        """
        returns the next Events
        """
        from open_municipio.events.models import Event
        return Event.future.filter(acts__id=self.id)

    @property
    def next_event(self):
        """
        returns the next Event or None
        """
        return self.next_events[0] if self.next_events else None

    @models.permalink
    def get_absolute_url(self):
        return ('om_cgdeliberation_detail', (), {'pk': str(self.pk)})



class Deliberation(Act):
    """
    WRITEME
    """
    INITIATIVE_TYPES = Choices(
        ('COUNSELOR', 'counselor', _('Counselor')),
        ('PRESIDENT', 'president', _('President')),
        ('ASSESSOR', 'assessor', _('City Government Member')),
        ('GOVERNMENT', 'government', _('City Government')),
        ('MAYOR', 'mayor', _('Mayor')),
    )

    FINAL_STATUSES = (
        ('APPROVED', _('approved')),
        ('REJECTED', _('rejected')),
    )

    STATUS = Choices(
        ('PRESENTED', 'presented', _('presented')),
        ('COMMITTEE', 'committee', _('committee')),
        ('COUNCIL', 'council', _('council')),
        ('APPROVED', 'approved', _('approved')),
        ('REJECTED', 'rejected', _('rejected')),
    )
    
    status = StatusField()
    approval_date = models.DateField(_('approval date'), null=True, blank=True)
    publication_date = models.DateField(_('publication date'), null=True, blank=True)
    final_idnum = models.CharField(max_length=64, blank=True, null=True, help_text=_("Internal identification string for the deliberation, when approved"))
    execution_date = models.DateField(_('execution date'), null=True, blank=True)
    initiative = models.CharField(_('initiative'), max_length=12, choices=INITIATIVE_TYPES)
    approved_text = models.TextField(blank=True)
    
    class Meta:
        verbose_name = _('deliberation')
        verbose_name_plural = _('deliberations')
        pass

    @property
    def next_events(self):
        """
        returns the next Events
        """
        from open_municipio.events.models import Event
        return Event.future.filter(acts__id=self.id)

    @property
    def next_event(self):
        """
        returns the next Event or None
        """
        return self.next_events[0] if self.next_events else None

    @models.permalink
    def get_absolute_url(self):
        return ('om_deliberation_detail', (), {'pk': str(self.pk)})
    

class Interrogation(Act):
    """
    WRITEME
    """
    ANSWER_TYPES = Choices(
        ('WRITTEN', 'written', _('Written')),
        ('VERBAL', 'verbal', _('Verbal')),
    )

    FINAL_STATUSES = (
        ('ANSWERED', _('answered')),
        ('NOTANSWERED', _('not answered')),
    )

    STATUS = Choices(
        ('PRESENTED', 'presented', _('presented')),
        ('ANSWERED', 'answered', _('answered')),
        ('NOTANSWERED', 'notanswered', _('not answered')),
    )
    
    status = StatusField()
    answer_type = models.CharField(_('answer type'), max_length=8, choices=ANSWER_TYPES)
    question_motivation = models.TextField(blank=True)
    answer_text = models.TextField(blank=True)
    reply_text = models.TextField(blank=True)

    class Meta:
        verbose_name = _('interrogation')
        verbose_name_plural = _('interrogations')
    
    @models.permalink
    def get_absolute_url(self):
        return 'om_interrogation_detail', (), {'pk': str(self.pk)}
    

class Interpellation(Act):
    """
    WRITEME
    """
    ANSWER_TYPES = Choices(
        ('WRITTEN', 'written', _('Written')),
        ('VERBAL', 'verbal', _('Verbal')),
    )

    FINAL_STATUSES = (
        ('ANSWERED', _('answered')),
        ('NOTANSWERED', _('not answered')),
    )

    STATUS = Choices(
        ('PRESENTED', 'presented', _('presented')),
        ('ANSWERED', 'answered', _('answered')),
        ('NOTANSWERED', 'notanswered', _('not answered')),
    )

    status = StatusField()
    answer_type = models.CharField(_('answer type'), max_length=8, choices=ANSWER_TYPES)
    question_motivation = models.TextField(blank=True)
    answer_text = models.TextField(blank=True)

    class Meta:
        verbose_name = _('interpellation')
        verbose_name_plural = _('interpellations')
    
    @models.permalink
    def get_absolute_url(self):
        return 'om_interpellation_detail', (), {'pk': str(self.pk)}
    

class Motion(Act):
    """
    It is a political act, used to publicly influence members of the City Government, or the Mayor,
    on a broad type of issues (specific to the Comune proceedings, or of a more general category)
    It is submitted to the Council approval and Emendations to it can be presented before the votation.
    """
    FINAL_STATUSES = (
        ('APPROVED', _('approved')),
        ('REJECTED', _('rejected')),
    )

    STATUS = Choices(
        ('PRESENTED', 'presented', _('presented')),
        ('COUNCIL', 'council', _('council')),
        ('APPROVED', 'approved', _('approved')),
        ('REJECTED', 'rejected', _('rejected')),
    )

    status = StatusField()
    
    class Meta:
        verbose_name = _('motion')
        verbose_name_plural = _('motions')
        
    @models.permalink
    def get_absolute_url(self):
        return ('om_motion_detail', (), {'pk': str(self.pk)})


class Agenda(Act):
    """
    Maps the *Ordine del Giorno* act type.
    It is a political act, used to publicly influence the following discussions on Deliberations.
    It is specifically used with respect to issues specific to the deliberation process.
    It is submitted to the Council approval and Emendations to it can be presented before the votation.
    """
    FINAL_STATUSES = (
        ('APPROVED', _('approved')),
        ('REJECTED', _('rejected')),
    )

    STATUS = Choices(
        ('PRESENTED', 'presented', _('presented')),
        ('COUNCIL', 'council', _('council')),
        ('APPROVED', 'approved', _('approved')),
        ('REJECTED', 'rejected', _('rejected')),
    )

    status = StatusField()

    class Meta:
        verbose_name = _('agenda')
        verbose_name_plural = _('agenda')

    @models.permalink
    def get_absolute_url(self):
        return ('om_agenda_detail', (), {'pk': str(self.pk)})


class Amendment(Act):
    """
    It is a modification of a particular act, that can be voted specifically and separately from the act itself.
    
    An emendation relates to an act, and it can relate theoretically to another emendation (sub-emendations).
    Optionally, an emendation relates to an act section (article, paragraph).
    """
    # TODO: add additional statuses allowed for this act type
    STATUS = Choices(
        ('PRESENTED', 'presented', _('presented')), 
        ('APPROVED', 'approved', _('approved'))
    )
    
    status = StatusField()
    act = models.ForeignKey(Act, related_name='amendment_set', on_delete=models.PROTECT)
    act_section = models.ForeignKey(ActSection, related_name='amendment_set', null=True, blank=True,
                                    on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('amendment')
        verbose_name_plural = _('amendments')


#
# Workflows
#
class Transition(models.Model):
    final_status = models.CharField(_('final status'), max_length=100)
    act = models.ForeignKey(Act, related_name='transition_set')
    votation = models.ForeignKey('votations.Votation', null=True, blank=True)
    transition_date = models.DateField(default=None)
    symbol = models.CharField(_('symbol'), max_length=128, blank=True, null=True)
    note = models.CharField(_('note'), max_length=255, blank=True, null=True)

    class Meta:
        db_table = u'acts_transition'
        verbose_name = _('status transition')
        verbose_name_plural = _('status transition')


#
# Documents
#

class Document(TimeStampedModel):
    """
    An abstract base class for all complex documents. 
    
    A document's content can be specified either as:
    
    * a text string
    * an URL to its textual representation
    * an URL to an external file
    * an uploaded internal file
    
    It is possible for a single document to have more than one type of content:
    for example, a textual and a PDF local versions, or remote links...
    """
    document_date = models.DateField(null=True, blank=True)
    document_type = models.CharField(max_length=5, null=True, blank=True)
    document_size = models.IntegerField(blank=True, null=True)
    text = models.TextField(blank=True)
    text_url = models.URLField(blank=True)
    file_url = models.URLField(blank=True)
    file = models.FileField(upload_to="attached_documents/%Y%m%d", blank=True, max_length=255)
    
    class Meta:
        abstract = True


class Attach(Document):
    """
    An attachment to a formal act. 

    Extends the ``Document`` class, by adding a title
    and a foreign key to the act the attachment relates to.
    """
    # FIXME: shouldn't this model be called ``Attachment`` instead ?
    title = models.CharField(max_length=255)
    act = models.ForeignKey(Act, related_name='attachment_set')

    class Meta(Document.Meta):
        verbose_name = _('attach')
        verbose_name_plural = _('attaches')
    
    def __unicode__(self):
        return u'%s' % self.title


#
# Speech
#
class Speech(Document):
    """
    A Speech is a special case of Attachment (it extends Document, too), that is connected
    to Acts, Votations and Charges and has field to map the audio content

    A Speech may be held by an external person, not mapped in our DB,
    in that case the ``author`` field may be left blank and the ``author_name_when_external``
    gets the name of the person
    """
    title = models.CharField(max_length=255, blank=True, null=True)
    sitting_item = models.ForeignKey('people.SittingItem')
    author = models.ForeignKey('people.Person', blank=True, null=True)
    author_name_when_external = models.CharField(max_length=255, blank=True, null=True)   
    votation = models.ForeignKey('votations.Votation', blank=True, null=True)
    related_act_set = models.ManyToManyField('Act', through='ActHasSpeech')
    initial_time = models.TimeField()
    duration = models.IntegerField(blank=True, null=True)
    seq_order = models.IntegerField(default=0)
    initial_time = models.TimeField(blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    audio_url = models.URLField(blank=True)
    audio_file = models.FileField(upload_to="attached_audio/%Y%m%d", blank=True, max_length=255)

    class Meta(Document.Meta):
        verbose_name = _('speech')
        verbose_name_plural = _('speeches')

    def __unicode__(self):
        return u'%s' % self.title

    @models.permalink
    def get_absolute_url(self):
        return('om_speech_detail', (), {'pk': str(self.pk)})

    @property
    def author_name(self):
        if self.author != None:
            return self.author

        return self.author_name_when_external

    @property
    def date(self):
        return self.sitting_item.sitting.date

    @property
    def sitting(self):    
        return self.sitting_item.sitting

    @property
    def author_counselor(self):
        politician = None
        try:
            politician = InstitutionCharge.objects.get(person=self.author,institution__institution_type=Institution.COUNCIL)
        except ObjectDoesNotExist:
            pass

        return politician

    @property
    def is_public(self):
        return self.act == None or self.act.status_is_final

    def __unicode__(self):
        return "%s - %s" % (self.author_name, self.sitting)

class ActHasSpeech(models.Model):
    """
    Relation between a speech and an act.
    A speech can be related to one or more acts.
    """
    RELATION_TYPE = Choices(
        ('REQ', 'request', _('request')),
        ('RESP', 'response', _('response')),
        ('REF', 'reference', _('reference')),
    )

    speech = models.ForeignKey('acts.Speech')
    act = models.ForeignKey('acts.Act')
    relation_type = models.CharField(choices=RELATION_TYPE, max_length=4)

    class Meta(Document.Meta):
        verbose_name = _('act mentioned in speech')
        verbose_name_plural = _('acts mentioned in speech')


#
# Calendar
#
class Calendar(models.Model):
    """
    WRITEME
    """
    act_set = models.ManyToManyField(Act)
    site = models.ForeignKey(Institution)
    date = models.DateField()

    class Meta:
        verbose_name = _('calendar')
        verbose_name_plural = _('calendar')

    @property
    def acts(self):
        return self.act_set.all()



#
# Signals handlers
#

logger = logging.getLogger('import')


@receiver(post_save, sender=ActSupport)
def new_signature(**kwargs):
    """
    generates a record in newscache, when an act is signed
    """
    # generates news only if not in raw mode (fixtures)
    # for signatures after presentation_date
    if not kwargs.get('raw', False):
        signature = kwargs['instance']
        act = signature.act.downcast()
        signer = signature.charge
        # define context for textual representation of the news
        ctx = Context({ 'current_site': Site.objects.get(id=settings.SITE_ID),
                        'signature': signature, 'act': act, 'signer': signer })

        # force convertion into strings of two date
        try:
            signature_support_date = signature.support_date.strftime("%Y-%m-%d")
        except:
            signature_support_date = signature.support_date

        try:
            act.presentation_date = act.presentation_date.strftime("%Y-%m-%d")
        except:
            act.presentation_date = act.presentation_date

        # generate new signature after presentation, for the act
        if signature.support_date > act.presentation_date:
            created = False
            news, created = News.objects.get_or_create(
                generating_object_pk=signature.pk,
                generating_content_type=ContentType.objects.get_for_model(signature),
                related_object_pk=act.pk,
                related_content_type=ContentType.objects.get_for_model(act),
                priority=3,
                text=News.get_text_for_news(ctx, 'newscache/act_signed_after_presentation.html')
            )
            if created:
                logger.debug("  act was signed after presentation news created")
            else:
                logger.debug("  act was signed after presentation news found")

        # generate signature news, for the politician
        created = False
        news, created = News.objects.get_or_create(
            generating_object_pk=signature.pk,
            generating_content_type=ContentType.objects.get_for_model(signature),
            related_object_pk=signer.pk,
            related_content_type=ContentType.objects.get_for_model(signer),
            priority=2,
            text=News.get_text_for_news(ctx, 'newscache/person_signed.html')
        )
        if created:
            logger.debug("  user signed act news created")
        else:
            logger.debug("  user signed act news found")


@receiver(pre_delete, sender=ActSupport)
def delete_signature(**kwargs):
    """
    remove all news generated by this signature, before removing the signature
    """
    if not kwargs.get('raw', False):
        signature = kwargs['instance']
        news = News.objects.filter(
            generating_object_pk=signature.pk,
            generating_content_type=ContentType.objects.get_for_model(signature),
        )
        n_news = news.count()
        news.delete()
        logger.debug("  %s news have been removed" % n_news)


@receiver(post_save, sender=Transition)
def new_transition(**kwargs):
    if not kwargs.get('raw', False):
        transition = kwargs['instance']
        act = transition.act.downcast()

        # modify act's status only when transition is created
        # avoid infinite loop
        if kwargs.get('created', False):
            # set act's status according to transition status
            act.status = transition.final_status
            act.save()
            # if it's a final status, set the according flag in the act's parent
            if act.is_final_status(act.status):
                act.act_ptr.status_is_final = True
                act.act_ptr.save()

        # generate news
        ctx = Context({ 'current_site': Site.objects.get(id=settings.SITE_ID),
                        'transition': transition, 'act': act })

        # handle presentation and other transitions differently,
        # to shorten acts' presentations, with signatures
        if transition.final_status == 'PRESENTED':
            created = False
            news, created = News.objects.get_or_create(
                generating_object_pk=transition.pk,
                generating_content_type=ContentType.objects.get_for_model(transition),
                related_object_pk=act.pk,
                related_content_type=ContentType.objects.get_for_model(act),
                priority=1,
                text=News.get_text_for_news(ctx, 'newscache/act_presented.html')
            )
            if created:
                logger.debug("  act presentation news created")
            else:
                logger.debug("  act presentation news found")

        else:
            created = False
            news, created = News.objects.get_or_create(
                generating_object_pk=transition.pk,
                generating_content_type=ContentType.objects.get_for_model(transition),
                related_object_pk=act.pk,
                related_content_type=ContentType.objects.get_for_model(act),
                priority=1,
                text=News.get_text_for_news(ctx, 'newscache/act_changed_status.html')
            )
            if created:
                logger.debug("  act changed status news created")
            else:
                logger.debug("  act changed status news found")

@receiver(pre_delete, sender=Transition)
def pre_delete_transition(**kwargs):
    """
    remove all news generated by this transition, before removing it
    """
    if not kwargs.get('raw', False):
        t = kwargs['instance']
        news = News.objects.filter(
            generating_object_pk=t.pk,
            generating_content_type=ContentType.objects.get_for_model(t),
            )
        n_news = news.count()
        news.delete()
        logger.debug("  %s news have been removed" % n_news)


@receiver(post_delete, sender=Transition)
def post_delete_transition(**kwargs):
    if not kwargs.get('raw', False):
        deleting_item = kwargs['instance']

        try:
            act = deleting_item.act.downcast()

            if act.get_last_transition():
                act.status = act.get_last_transition().final_status
                if act.is_final_status(deleting_item.final_status):
                    act.status_is_final = False

                act.save()
        except ObjectDoesNotExist:
            pass

