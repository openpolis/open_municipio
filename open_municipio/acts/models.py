# -*- coding: utf-8 -*-
from south.modelsinspector import add_ignored_fields
from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.template.context import Context
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from model_utils import Choices
from model_utils.managers import InheritanceManager, QueryManager
from model_utils.models import TimeStampedModel
from model_utils.fields import StatusField

from open_municipio.acts.exceptions import WorkflowError
from open_municipio.acts.signals import act_presented, act_signed, act_status_changed
from open_municipio.newscache.models import News, NewsTargetMixin
from open_municipio.people.models import Institution, InstitutionCharge, Sitting, Person
from open_municipio.taxonomy.managers import TopicableManager
from open_municipio.taxonomy.models import Category, TaggedAct
from open_municipio.locations.models import Location, TaggedActByLocation
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
    # internal ID string for this act within a given municipality
    idnum = models.CharField(max_length=64, blank=True, help_text=_("A string representing the identification or sequence number for this act, used internally by the municipality's administration."))
    # official act title, as defined by the municipality
    title = models.CharField(_('title'), max_length=255, blank=True)
    # editorial (descriptive) act title
    adj_title = models.CharField(_('adjoint title'), max_length=255, blank=True, help_text=_("An adjoint title, added to further explain an otherwise cryptic title"))
    # when this act was officially presented
    presentation_date = models.DateField(_('presentation date'), null=True, help_text=_("Date of presentation, as stated in the act"))
    # a textual description for this act
    description = models.TextField(_('description'), blank=True)
    # official act text
    text = models.TextField(_('text'), blank=True)
    # which people presented this act
    presenter_set = models.ManyToManyField(InstitutionCharge, blank=True, null=True, through='ActSupport', related_name='presented_act_set', verbose_name=_('presenters'))
    # intended recipients for this act (if any)
    recipient_set = models.ManyToManyField(InstitutionCharge, blank=True, null=True, related_name='received_act_set', verbose_name=_('recipients'))
    # the instititution which emitted this act
    emitting_institution = models.ForeignKey(Institution, related_name='emitted_act_set', verbose_name=_('emitting institution'))
    # categories associated to this act
    category_set = models.ManyToManyField(Category, verbose_name=_('categories'), blank=True, null=True)
    # locations associated to this act
    location_set = models.ManyToManyField(Location, through=TaggedActByLocation, verbose_name=_('locations'), blank=True, null=True)
    # whether this act has reached a final (definitive) status
    status_is_final = models.BooleanField(default=False)
    # wheter this act is a "key" one
    is_key = models.BooleanField(default=False, help_text=_("Specify whether this act should be featured"))
    # default manager
    objects = InheritanceManager()
    # use this manager to retrieve only key acts
    featured = QueryManager(is_key=True).order_by('-presentation_date') 
    # tags associated to this act
    tag_set = TopicableManager(through=TaggedAct, blank=True)
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
    
    def save(self, *args, **kwargs):
        # update ``status_is_final`` cache field
        self._update_status_is_final()
        super(Act, self).save(*args, **kwargs)
   
    def get_absolute_url(self):
        return self.downcast().get_absolute_url()
    
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
        #return set([ topic.tag for topic in self.topics ])
        return self.tag_set.all()
    
    @property
    def categories(self):
        # FIXME: cleanup needed, here!
        return list( set([ topic.category for topic in self.topics]) )
        #return self.category_set.all()

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

    @property    
    def status(self):
        """
        Return the current status of a *concrete* act instance.
        
        If this property is being accessed from an ``Act`` instance,
        raise ``AttributeError``.
        """
        # retrieving the current status makes only sense for a concrete act instance
        if not self._meta.object_name == 'Act':
            return self._status
        else:
            raise AttributeError("Only concrete act instances have a `status' attribute")
        
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
            if groups.has_key(transition.target_status):
                groups.get(transition.target_status).append(transition)
        return groups

    def is_final_status(self, status=None):
        """
        Return ``True`` iff the ``status`` argument is a final status for this act instance. 
        
        If no ``status`` argument is provided, checks if the *current status* for this act
        is a final one.
        
        This method only makes sense for concrete act instances: when invoked from an ``Act``
        instance, raise ``AttributeError``.
        """ 
        if not self._meta.object_name == 'Act':
            # checking for final statuses only makes sense for concrete act instances
            status = status or self.status
            if status in [t[0] for t in self.FINAL_STATUSES]:     
                return True
            else:
                return False
        else:
            raise AttributeError("`is_final_status()` may only be accessed from concrete act instances")       
   
    def _update_status_is_final(self):
        """
        Update the ``status_is_final`` cache field based on the current act status.
        
        This method only makes sense for concrete act instances: when invoked from an ``Act``
        instance, raise ``AttributeError``.
        """ 
        if not self._meta.object_name == 'Act':
            # this makes sense only for concrete act instances
            if self.is_final_status():
                self.status_is_final = True
            else:
                self.status_is_final = False
        else:
            raise AttributeError("This method may only be invoked from concrete act instances")
    
    @property
    def last_transition(self):
        """
        Return the last created transition for this act.
        
        If no transitions are associated to this act, return ``None``
        """
        if self.transitions:
            return self.transitions.order_by('-transition_date')[0]
        else:
            return None

    def get_status_display(self):
        """
        WRITEME
        """
        return self.downcast().get_status_display()

    def get_type_name(self):
        """
        WRITEME
        """
        return self.downcast()._meta.verbose_name


## Signal handlers
@receiver(post_save, sender=Act)
def signal_act_presented(self, **kwargs):
    """
    Notify the system when a new act has been presented,
    by sending an ``act_presented`` signal.
    
    .. note::
    
        This signal is being sent only *after* a *new* act has been created, 
        (not when an act has been updated), and only after the fixture-loading phase.
        
    """
    raw = kwargs.get('raw')
    created = kwargs.get('created')
    if not raw and created:
        act_presented.send(sender=self)


class ActSection(models.Model):
    """
    A section (or sub-section) of an act's text content.

    .. note::
    
    Currently, this feature is not being used, but it likely be in future releases

    """
    act = models.ForeignKey(Act, on_delete=models.PROTECT)
    parent_section = models.ForeignKey('self', on_delete=models.PROTECT)  
    title = models.CharField(max_length=128, blank=True)
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
    # who signed the act (a politician)
    charge = models.ForeignKey(InstitutionCharge)
    # the act being signed
    act = models.ForeignKey(Act)
    # type of support being provided by the signer to the act
    support_type = models.CharField(choices=SUPPORT_TYPE, max_length=12)
    # when the act was signed
    support_date = models.DateField(_('support date'), default=None, blank=True, null=True)

    class Meta:
        db_table = u'acts_act_support'
    
    def save(self, *args, **kwargs):        
        super(ActSupport, self).save(*args, **kwargs)
        # signal that a new act has been signed
        act_signed.send(sender=self)


class ActDescriptor(TimeStampedModel):
    """
    A relationship mapping politicians who added or modified an act's description.
    """
    person = models.ForeignKey(Person)
    act = models.ForeignKey(Act)

    class Meta:
        db_table = u'acts_act_descriptor'



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
    
    _status = StatusField()
    approval_date = models.DateField(_('approval date'), null=True, blank=True)
    publication_date = models.DateField(_('publication date'), null=True, blank=True)
    execution_date = models.DateField(_('execution date'), null=True, blank=True)
    initiative = models.CharField(_('initiative'), max_length=12, choices=INITIATIVE_TYPES)
    approved_text = models.TextField(blank=True)
    
    class Meta:
        verbose_name = _('deliberation')
        verbose_name_plural = _('deliberations')

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
    
    _status = StatusField()
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

    _status = StatusField()
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

    _status = StatusField()
    
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

    _status = StatusField()

    class Meta:
        verbose_name = _('agenda')
        verbose_name_plural = _('agenda')

    @models.permalink
    def get_absolute_url(self):
        return ('om_agenda_detail', (), {'pk': str(self.pk)})


class Emendation(Act):
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
    
    _status = StatusField()
    act = models.ForeignKey(Act, related_name='emendation_set', on_delete=models.PROTECT)
    act_section = models.ForeignKey(ActSection, related_name='emendation_set', null=True, blank=True, 
                                    on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('emendation')
        verbose_name_plural = _('emendations')



#
# Workflows
#
class Transition(models.Model):
    target_status = models.CharField(_('target status'), max_length=100)
    act = models.ForeignKey(Act, related_name='transition_set')
    votation = models.ForeignKey('votations.Votation', null=True, blank=True)
    transition_date = models.DateField(default=None)
    symbol = models.CharField(_('symbol'), max_length=128, blank=True, null=True)
    note = models.CharField(_('note'), max_length=255, blank=True, null=True)

    class Meta:
        db_table = u'acts_transition'
        verbose_name = _('status transition')
        verbose_name_plural = _('status transition')

        
## Signal handlers

@receiver(act_presented)
def create_initial_transition(sender, **kwargs):
    """
    When an act reaches its initial status (i.e. when it's presented),
    create the initial transition.
    
    .. note::
    
        This routine won't be performed during the fixture-loading phase.
    
    """
    # the ``sender`` of this signal is a concrete act instance
    act = sender
    Transition.object.create(
            act=act.act_ptr,
            target_status=act.STATUS.presented,
            transition_date=act.presentation_date,
            )

    
@receiver(post_save, sender=Transition)
def update_act_status(**kwargs):
    """
    When a *new* transition has been *created*, perform the following tasks:
    
    #. update act current status
    #. notify the system about that status change, by sending an 
       ``act_status_changed`` signal.
    
    .. note::
    
        This routine will be performed only *after* a *new* transition has been created, 
        and only after the fixture-loading phase.
        
    """
    raw = kwargs.get('raw')
    created = kwargs.get('created')
    if not raw and created:
        # update current act status
        transition = kwargs.get('instance')
        act = transition.act.downcast()
        act._status = transition.target_status
        act.save()
        # signal the status change 
        act_status_changed.send(sender=self)

        
@receiver(pre_delete, sender=Transition)
def revert_act_status(**kwargs):
    """
    Before a transition being deleted from the DB, accordingly revert the status 
    of its associated act.
    """   
    transition = kwargs['instance']
    act = transition.act.downcast()
    if act.last_transition:
        act._status = act.last_transition.target_status
    else: 
        # no more transitions would exist for this act
        # this may happen only if the initial transition 
        # (created when an act "reaches" its initial status)
        # will be deleted from the DB, leaving that act in an "undefined" status
        # this is a patologic condition, so an exception should be raised here
        raise WorkflowError("You cannot delete the first transition for act %s" % act)
    act.save()


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
    file = models.FileField(upload_to="attached_documents/%Y%d%m", blank=True)
    
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
  

class Minute(Document):
    """
    WRITEME
    """
    sitting = models.ForeignKey(Sitting)
    act_set = models.ManyToManyField(Act)    
    
    class Meta(Document.Meta):
        verbose_name = _('minute')
        verbose_name_plural = _('minutes')

    @property
    def acts(self):
        return self.act_set.all()


class Outcome(models.Model):
    """
    WRITEME
    """
    sitting = models.ForeignKey(Sitting)
    act_set = models.ManyToManyField(Act)    

    class Meta(Document.Meta):
        verbose_name = _('outcome')
        verbose_name_plural = _('outcomes')

    @property
    def acts(self):
        return self.act_set.all()
        
        
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