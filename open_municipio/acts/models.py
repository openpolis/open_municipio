# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from model_utils import Choices
from model_utils.managers import InheritanceManager, QueryManager
from model_utils.models import TimeStampedModel
from model_utils.fields import StatusField

from south.modelsinspector import add_ignored_fields

from open_municipio.acts.exceptions import WorkflowError
from open_municipio.acts.signals import act_presented, act_signed, act_status_changed
from open_municipio.newscache.models import NewsTargetMixin
from open_municipio.people.models import Institution, InstitutionCharge, Sitting, Person
from open_municipio.taxonomy.managers import TopicableManager
from open_municipio.taxonomy.models import Category, TaggedAct
from open_municipio.locations.models import Location, TaggedActByLocation
from open_municipio.monitoring.models import MonitorizedItem


#
# Acts
#

class Act(NewsTargetMixin, MonitorizedItem, TimeStampedModel):
    """
    This is the base class for all the different act types: it contains the common fields for
    deliberations, interrogations, interpellations, motions, agendas and emendations.
  
    It is a ``TimeStampedModel``, so it tracks creation and modification timestamps for each record.

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
    # wheter this act is a "key" one
    is_key = models.BooleanField(default=False, help_text=_("Specify whether this act should be featured"))
    # default manager
    objects = InheritanceManager()
    # use this manager to retrieve only key acts
    featured = QueryManager(is_key=True).order_by('-presentation_date') 
    # tags associated to this act
    tag_set = TopicableManager(through=TaggedAct, blank=True)

    def __unicode__(self):
        rv = u'%s' % (self.title, )
        if self.idnum:
            rv = u'%s - %s' % (self.idnum, rv)
        if self.adj_title:
            rv = u'%s (%s)' % (rv, self.adj_title)
        return rv
                
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
        """
        A queryset of attachments linked to this act.
        """
        return self.attachment_set.all()

    @property
    def transitions(self):
        """
        A queryset of transitions that this act underwent.
        """
        return self.transition_set.all()

    @property
    def presenters(self):
        """
        A queryset of institutional charge(s) by which this act has been presented.
        """
        return self.presenter_set.all()

    @property
    def recipients(self):
        """
        A queryset of institutional charge(s) to which this act was addressed.
        """
        return self.recipient_set.all()
    
    @property
    def first_signers(self):
        """
        A queryset of institutional charge(s) which signed this act.
        """
        # FIXME: resolve asymmetry between this query and that for ``co_signers`` property
        return InstitutionCharge.objects.filter(actsupport__act__id = self.pk,
                                                actsupport__support_type=ActSupport.SUPPORT_TYPE.first_signer)
    @property
    def co_signers(self):
        """
        A queryset of institutional charge(s) which co-signed this act.
        """
        # FIXME: resolve asymmetry between this query and that for ``first_signers`` property
        return self.presenter_set.filter(actsupport__support_type=ActSupport.SUPPORT_TYPE.co_signer)

    @property
    def emendations(self):
        """
        A queryset of amendements presented against this act.
        """
        return self.emendation_set.all()
    
    ##---- Taxonomy ----##
    @property
    def tags(self):
        """
        A queryset of tags used to classify this act. 
        """
        # FIXME: cleanup needed, here!
        #return set([ topic.tag for topic in self.topics ])
        return self.tag_set.all()
    
    @property
    def categories(self):
        """
        A queryset of categories used to classify this act. 
        """
        # FIXME: cleanup needed, here!
        return list( set([ topic.category for topic in self.topics]) )
        #return self.category_set.all()

    @property
    def topics(self):
        """
        A queryset of topics (tags + categories) used to classify this act. 
        """
        return self.tag_set.topics()
    
    @property
    def locations(self):
        """
        A queryset of locations used to classify this act. 
        """
        return self.location_set.all()
    
    ##---- End taxonomy ----##
    
    @property
    def act_descriptors(self):
        """
        A queryset of all those users which modified this act's description.
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

    def get_type_name(self):
        """
        WRITEME
        """
        return self.downcast()._meta.verbose_name


class ActStatusMixin(models.Model):
    """
    An abstract, mixin model class encapsulating workflow-related data & logic
    shared by every *concrete* ``Act`` subclass.
    """
    # current act status
    _status = StatusField()
    # whether this act has reached a final (definitive) status
    status_is_final = models.BooleanField(default=False)
      
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # update ``status_is_final`` cache field
        self._update_status_is_final()
        # call base implementation of ``save()`` method
        super(Act, self).save(*args, **kwargs)
        # signal creation ("presentation") of a new act
        self._signal_act_presented(**kwargs)
   
    def _signal_act_presented(self, **kwargs):
        """
        Notifies the system when a new act has been presented,
        by sending an ``act_presented`` signal.
        
        .. note::
        
            This signal is being sent only *after* a *new* act has been created, 
            (not when an act has been updated), and only after the fixture-loading phase.
           
        """
        raw = kwargs['raw']
        created = kwargs['created']
        if not raw and created:
            act_presented.send(sender=self)

    @property    
    def status(self):
        """
        Returns the current status of this act instance.
        """
        return self._status
        
    def get_transitions_groups(self):
        """
        Returns a dictionary having as keys the allowed statuses 
        for this act instance, and as values a queryset of transitions 
        having that target status, in reverse chronological order.
        """
        groups = {}
        states = [t[0] for t in self.STATUS]
        for state in states:
            groups[state] = self.transitions.filter(target_status=state).order_by('-transition_date')
        return groups
    
    def _update_status(self):
        """
        Updates this act's status based on the corresponding set of transitions.
        
        Note that, by definition, an act's status is the target status 
        of the last transition occurred to it. 
        """
        self._status = self.last_transition.target_status
        self.save()
        

    def is_final_status(self, status=None):
        """
        Returns ``True`` iff the ``status`` argument is a final status for this act instance. 
        
        If no ``status`` argument is provided, check if the *current status* for this act
        is a final one.
        """ 
        status = status or self.status
        final_statuses = [t[0] for t in self.FINAL_STATUSES]
        return status in final_statuses     
   
    def _update_status_is_final(self):
        """
        Updates the ``status_is_final`` cache field based on the current act status.
        """ 
        if self.is_final_status():
            self.status_is_final = True
        else:
            self.status_is_final = False
    
    @property
    def last_transition(self):
        """
        Returns the last created transition for this act.
        
        If no transitions are associated to this act, return ``None``.
        """
        if self.transitions.count():
            return self.transitions.order_by('-transition_date')[0]
        else:
            return None
   

class ActSection(models.Model):
    """
    A section (or sub-section) of an act's textual content.

    .. note::
    
        Currently this model is unused, but this will change in future releases.

    """
    # the act this section belongs to
    act = models.ForeignKey(Act, on_delete=models.PROTECT)
    # the parent section (if any)
    # used to model acts' sub-section, sub-sub-section, etc.
    parent_section = models.ForeignKey('self', on_delete=models.PROTECT)
    # section's title  
    title = models.CharField(max_length=128, blank=True)
    # section's content
    text = models.TextField(blank=True)
  
    def __unicode__(self):
        return u'%s' % self.title

    class Meta:
        db_table = u'acts_act_section'

    @property
    def emendations(self):
        """
        A queryset of amendements presented against this section.
        """
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
        self._signal_act_signed(**kwargs)
    
    def _signal_act_signed(self, **kwargs):
        """
        Notifies the system when an act has been signed, 
        by sending an ``act_signed`` signal.
        
        .. note::
        
            This signal is being sent only *after* an act has been signed, 
            and only after the fixture-loading phase.          

        """
        raw = kwargs['raw']
        created = kwargs['created']
        if not raw and created:
            act_signed.send(sender=self)


class ActDescriptor(TimeStampedModel):
    """
    A relationship mapping politicians who added or modified an act's description. 
    """
    # who modified the act's description
    person = models.ForeignKey(Person)
    # the act whose description has been modified 
    act = models.ForeignKey(Act)

    class Meta:
        db_table = u'acts_act_descriptor'



class Deliberation(ActStatusMixin, Act):
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
    # when the deliberation was approved
    approval_date = models.DateField(_('approval date'), null=True, blank=True)
    # when the deliberation was published
    publication_date = models.DateField(_('publication date'), null=True, blank=True)
    # from when the deliberation will become executive
    execution_date = models.DateField(_('execution date'), null=True, blank=True)
    # initiative type for this deliberation
    initiative = models.CharField(_('initiative'), max_length=12, choices=INITIATIVE_TYPES)
    # approved deliberation text
    approved_text = models.TextField(blank=True)
    
    class Meta:
        verbose_name = _('deliberation')
        verbose_name_plural = _('deliberations')

    @models.permalink
    def get_absolute_url(self):
        return ('om_deliberation_detail', (), {'pk': str(self.pk)})
    

class Interrogation(ActStatusMixin, Act):
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
    
    # how this interrogation will be answered by its recipient(s) (verbally or in writing) 
    answer_type = models.CharField(_('answer type'), max_length=8, choices=ANSWER_TYPES)
    # motivation for issuing this interrogation
    question_motivation = models.TextField(blank=True)
    # content of the recipient's answer
    answer_text = models.TextField(blank=True)
    # content of the presenter's reply
    reply_text = models.TextField(blank=True)

    class Meta:
        verbose_name = _('interrogation')
        verbose_name_plural = _('interrogations')
    
    @models.permalink
    def get_absolute_url(self):
        return 'om_interrogation_detail', (), {'pk': str(self.pk)}
    

class Interpellation(ActStatusMixin, Act):
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

    # how this interpellation will be answered by its recipient(s) (verbally or in writing)
    answer_type = models.CharField(_('answer type'), max_length=8, choices=ANSWER_TYPES)
    # motivation for issuing this interrogation
    question_motivation = models.TextField(blank=True)
    # content of the recipient's answer
    answer_text = models.TextField(blank=True)

    class Meta:
        verbose_name = _('interpellation')
        verbose_name_plural = _('interpellations')
    
    @models.permalink
    def get_absolute_url(self):
        return 'om_interpellation_detail', (), {'pk': str(self.pk)}
    

class Motion(ActStatusMixin, Act):
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

    
    class Meta:
        verbose_name = _('motion')
        verbose_name_plural = _('motions')
        
    @models.permalink
    def get_absolute_url(self):
        return ('om_motion_detail', (), {'pk': str(self.pk)})


class Agenda(ActStatusMixin, Act):
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


    class Meta:
        verbose_name = _('agenda')
        verbose_name_plural = _('agenda')

    @models.permalink
    def get_absolute_url(self):
        return ('om_agenda_detail', (), {'pk': str(self.pk)})


class Emendation(ActStatusMixin, Act):
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
    # the act against which this amendement was proposed
    act = models.ForeignKey(Act, related_name='emendation_set', on_delete=models.PROTECT)
    # the act's section (if any) against which this amendement was proposed 
    act_section = models.ForeignKey(ActSection, related_name='emendation_set', null=True, blank=True, 
                                    on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('emendation')
        verbose_name_plural = _('emendations')



#
# Workflows
#
class Transition(models.Model):
    """
    This model tracks acts' status changes: when an act changes its status,
    a new transition is generated.
    
    Transitions objects store the following pieces of information:
    
    * the act changing its status
    * the final (target) act's status
    * when the transition happened [*]_
    * an optional symbol (encoding the transition's type)
    * the votation which generated that transition (if any)
    * an optional note for recording transition-specific additional details
       
    
    .. [*] Since the time granularity is one day, taking into account that an act may 
        undergo two o more transitions on the same day, it may well happen that two distinct
        transitions (related to the same act) share an identical ``transition_date`` attribute.
    
    """
    # the final status for the act
    target_status = models.CharField(_('target status'), max_length=100)
    # the act which underwent a status change
    act = models.ForeignKey(Act, related_name='transition_set')
    # the votation which generated this transition (if any)
    votation = models.ForeignKey('votation.Votation', null=True, blank=True)
    # when the transition happened
    transition_date = models.DateField(default=None)
    # an optional symbol encoding the transition type
    symbol = models.CharField(_('symbol'), max_length=128, blank=True)
    # some additional details about the transition (if any)
    note = models.CharField(_('note'), max_length=255, blank=True)

    class Meta:
        db_table = u'acts_transition'
        verbose_name = _('status transition')
        verbose_name_plural = _('status transitions')

    def get_previous(self):
        """
        Return the previous transition (i.e. that happened just before this one, if any).
        
        If this is the initial transition for a given act, return ``None``.
        """
        # TODO: add model-level caching
        # retrieve all the transitions happened before this one (*including* itself)
        # note that we have to use the ``lte`` lookup filter since two transitions may
        # happen the same day
        previous = Transition.objects.filter(act=self.act, transition_date__lte=self.transition_date)\
                                      .order_by('-transition_date')
        if previous.count() == 1: # initial transition
            return None
        else:
            return previous[1]  
    
    def get_next(self):
        """
        Return the next transition (i.e. that happened just after this one, if any).
        
        If this is the last transition for a given act, return ``None``.
        """
        # TODO: add model-level caching
        # retrieve the all the transitions happened after this one (*including* itself)
        # note that we have to use the ``gte`` lookup filter since two transitions may
        # happen the same day
        next = Transition.objects.filter(act=self.act, transition_date__gte=self.transition_date)\
                                  .order_by('transition_date')
        if next.count() == 1: # last transition
            return None
        else:
            return next[1]  
    
    @property
    def is_initial(self):
        """
        Return ``True`` if this transition is the initial one; ``False`` otherwise.
        """
        # TODO: add model-level caching
        return not self.get_previous()       
    
    @property
    def is_final(self):
        """
        Return ``True`` if this transition is the final one; ``False`` otherwise.
        """
        # TODO: add model-level caching
        return not self.get_next()
   
    
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
    Transition.objects.create(
            act=act.act_ptr,
            target_status=act.STATUS.presented,
            transition_date=act.presentation_date,
            )

    
@receiver(post_save, sender=Transition)
def update_act_status(sender, **kwargs):
    """
    When a *new* transition has been *created*, perform the following tasks:
    
    #. update act's current status
    #. notify the system about that status change, by sending an 
       ``act_status_changed`` signal.
    
    .. note::
    
        This routine will be performed only *after* a *new* transition has been created, 
        and only after the fixture-loading phase.
        
    """
    raw = kwargs['raw']
    created = kwargs['created']
    if not raw and created:
        # update current act status
        transition = kwargs['instance']
        act = transition.act.downcast()
        act._update_status()
        # signal the status change 
        act_status_changed.send(sender=act)

        
@receiver(pre_delete, sender=Transition)
def revert_act_status(sender, **kwargs):
    """
    Before a transition being deleted from the DB, accordingly revert the status 
    of its associated act.
    
    .. note::

        Deleting the *initial transition* -- the one which had been created
        when the act "reached" its initial status -- should be considered an illegal operation, 
        since doing so would leave the act in an "undefined" status, a pathological condition 
        that must be avoided.  
        
        So, the action of deleting such a transition triggers a ``WorkflowError`` exception.
         
    """   
    transition = kwargs['instance']
    act = transition.act.downcast()
    if transition.is_initial:
        raise WorkflowError("Cannot delete initial transition")
    else:
        act = transition.act.downcast()
        act._status = transition.get_previous().target_status
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
    # when the document was authored/published
    document_date = models.DateField(null=True, blank=True)
    # document's type
    document_type = models.CharField(max_length=5, blank=True)
    # size of the document
    document_size = models.IntegerField(blank=True, null=True)
    # document's textual content
    text = models.TextField(blank=True)
    # URL pointing to the document's textual content
    text_url = models.URLField(blank=True)
    # document's file
    file = models.FileField(upload_to="attached_documents/%Y%d%m", blank=True)
    # URL pointing to the document's file
    file_url = models.URLField(blank=True)
    
    
    class Meta:
        abstract = True


class Attach(Document):
    """
    An attachment to a formal act. 

    It's just a document with a title, linking to an existing act.
    """
    # FIXME: shouldn't this model be called ``Attachment`` instead ?
    # a title for the attachment
    title = models.CharField(max_length=255)
    # the act this document is attached to
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
    # the sitting this document refers to
    sitting = models.ForeignKey(Sitting)
    # the set of acts referenced by this document
    act_set = models.ManyToManyField(Act)    
    
    class Meta(Document.Meta):
        verbose_name = _('minute')
        verbose_name_plural = _('minutes')

    @property
    def acts(self):
        """
        A queryset of acts referenced by this minute.
        """
        return self.act_set.all()


class Outcome(models.Model):
    """
    WRITEME
    """
    # the sitting this document refers to
    sitting = models.ForeignKey(Sitting)
    # the set of acts referenced by this document
    act_set = models.ManyToManyField(Act)    

    class Meta(Document.Meta):
        verbose_name = _('outcome')
        verbose_name_plural = _('outcomes')

    @property
    def acts(self):
        """
        A queryset of acts referenced by this minute.
        """
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