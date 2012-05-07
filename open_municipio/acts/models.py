# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.template.context import Context
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from model_utils import Choices
from model_utils.managers import InheritanceManager, QueryManager
from model_utils.models import TimeStampedModel
from model_utils.fields import StatusField

from open_municipio.newscache.models import News, NewsTargetMixin

from open_municipio.people.models import Institution, InstitutionCharge, Sitting, Person
from open_municipio.taxonomy.managers import TopicableManager
from open_municipio.taxonomy.models import Category, TaggedAct
from open_municipio.locations.models import Location, TaggedActByLocation
from open_municipio.monitoring.models import Monitoring, MonitorizedItem


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
    The default manager is the ``InheritanceManager`` (from package ``django-model-utils``_),
    that enables the ``select_subclasses()`` method, allowing the retrieval of subclasses, when needed.


    .. _django-model-utils: https://bitbucket.org/carljm/django-model-utils/src

    """

    idnum = models.CharField(max_length=64, blank=True, help_text=_("A string representing the identification number or sequence, used internally by the administration."))
    title = models.CharField(_('title'), max_length=255, blank=True)
    adj_title = models.CharField(_('adjoint title'), max_length=255, blank=True, help_text=_("An adjoint title, added to further explain an otherwise cryptic title"))
    presentation_date = models.DateField(_('presentation date'), null=True, help_text=_("Date of presentation, as stated in the act"))
    description = models.TextField(_('description'), blank=True)
    text = models.TextField(_('text'), blank=True)
    presenter_set = models.ManyToManyField(InstitutionCharge, blank=True, null=True, through='ActSupport', related_name='presented_act_set', verbose_name=_('presenters'))
    recipient_set = models.ManyToManyField(InstitutionCharge, blank=True, null=True, related_name='received_act_set', verbose_name=_('recipients'))
    emitting_institution = models.ForeignKey(Institution, related_name='emitted_act_set', verbose_name=_('emitting institution'))
    category_set = models.ManyToManyField(Category, verbose_name=_('categories'), blank=True, null=True)
    location_set = models.ManyToManyField(Location, through=TaggedActByLocation, verbose_name=_('locations'), blank=True, null=True)
    status_is_final = models.BooleanField(default=False)
    is_key = models.BooleanField(default=False, help_text=_("Specify whether this act should be featured"))

    objects = InheritanceManager()
    # use this manager to retrieve only key acts
    featured = QueryManager(is_key=True).order_by('-presentation_date') 
    
    tag_set = TopicableManager(through=TaggedAct, blank=True)

    # manager to handle the list of monitoring having as content_object this instance
    monitoring_set = generic.GenericRelation(Monitoring, object_id_field='object_pk')

    def __unicode__(self):
        uc = u'%s' % (self.title, )
        if self.idnum:
            uc = u'%s - %s' % (self.idnum, uc)
        if self.adj_title:
            uc = u'%s (%s)' % (uc, self.adj_title)
        return uc
     
    def downcast(self):
        """
        Returns the "downcasted"[*]_ version of this model instance.
        
        .. [*]: In a multi-table model inheritance scenario, the term "downcasting"
                refers to the process to retrieve the child model instance given the 
                parent model instance.
        """
        # FIXME: this check is redundant, IMO (seldon)
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
        return InstitutionCharge.objects.filter(actsupport__act__id = self.pk,
                                                actsupport__support_type=ActSupport.SUPPORT_TYPE.first_signer)                                            
    
    @property
    def co_signers(self):
        return self.presenter_set.filter(actsupport__support_type=ActSupport.SUPPORT_TYPE.co_signer)
        
    @property
    def tags(self):
        #return set([ topic.tag for topic in self.topics ])
        return self.tag_set.all()
    
    @property
    def categories(self):
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
        Returns the queryset of all those that modified the description
        """
        return self.actdescriptor_set.all()

    @property
    def content_type_id(self):
        """
        Returns id of the content type associated with this instance.
        """
        return ContentType.objects.get_for_model(self).id

    def status(self):
        """
        Returns the current status for the downcasted version of this act instance.
        
        Note: it seems that this method cannot be made into a property,
        since doing that raises a ``AttributeError: can't set attribute``
        exception during Django initialization. 
        """
        return self.downcast().status
        
    def get_transitions_groups(self):
        """
        retrieve a list of transitions grouped by status
        """
        groups = {}
        this = self.downcast()
        if not hasattr(this, 'STATUS'):
            return groups

        # initialize all status with an empty list of transitions
        for status in this.STATUS:
            groups[status[0]] = []

        # fill groups with ordered transitions
        for transition in this.transition_set.all().order_by('-transition_date'):
            if groups.has_key(transition.final_status):
                groups.get(transition.final_status).append(transition)
        return groups

    def is_final_status(self, status=None):
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
        if self.transitions:
            return list(self.transitions)[-1]
        return False

    def get_absolute_url(self):
        return self.downcast().get_absolute_url()

      
class ActSection(models.Model):
    """
    This describes a section (or sub-section) of an act text.
    This feature will likely be used in future releases.
    """
    act = models.ForeignKey(Act, on_delete=models.PROTECT)
    parent_section = models.ForeignKey('self', on_delete=models.PROTECT)  
    title = models.CharField(max_length=128, blank=True)
    text = models.TextField(blank=True)
  
    def __unicode__(self):
        return u'%s' % self.title

    class Meta:
        db_table = u'acts_act_section'


class ActSupport(models.Model):
    """
    Maps the signers of the act (supporters)
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
    Maps the politicians that added or modified the description of the act.
    """
    person = models.ForeignKey(Person)
    act = models.ForeignKey(Act)

    class Meta:
        db_table = u'acts_act_descriptor'



class Deliberation(Act):
    """
    WRITEME
    """
    INIZIATIVE_CHOICES = Choices(
        ('COUNSELOR', 'counselor', _('Counselor')),
        ('PRESIDENT', 'president', _('President')),
        ('ASSESSOR', 'assessor', _('City Government Member')),
        ('GOVERNMENT', 'government', _('City Government')),
        ('MAYOR', 'mayor', _('Mayor')),
    )

    FINAL_STATUSES = [
        ('APPROVED', _('approved')),
        ('REJECTED', _('rejected')),
    ]

    STATUS = Choices(
        ('PRESENTED', 'presented', _('presented')),
        ('COMMITTEE', 'committee', _('committee')),
        ('COUNCIL', 'council', _('council')),
        (FINAL_STATUSES[0][0], 'approved', FINAL_STATUSES[0][1]),
        (FINAL_STATUSES[1][0], 'rejected', FINAL_STATUSES[1][1]),
    )
    
    status = StatusField()
    approval_date = models.DateField(_('approval date'), null=True, blank=True)
    publication_date = models.DateField(_('publication date'), null=True, blank=True)
    execution_date = models.DateField(_('execution date'), null=True, blank=True)
    initiative = models.CharField(_('initiative'), max_length=12, choices=INIZIATIVE_CHOICES)
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

    FINAL_STATUSES = [
        ('ANSWERED', _('answered')),
        ('NOTANSWERED', _('not answered')),
    ]

    STATUS = Choices(
        ('PRESENTED', 'presented', _('presented')),
        (FINAL_STATUSES[0][0], 'answered', FINAL_STATUSES[0][1]),
        (FINAL_STATUSES[1][0], 'notanswered', FINAL_STATUSES[1][1]),
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
    FINAL_STATUSES = [
        ('ANSWERED', _('answered')),
        ('NOTANSWERED', _('not answered')),
    ]

    STATUS = Choices(
        ('PRESENTED', 'presented', _('presented')),
        (FINAL_STATUSES[0][0], 'answered', FINAL_STATUSES[0][1]),
        (FINAL_STATUSES[1][0], 'notanswered', FINAL_STATUSES[1][1]),
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
    STATUS = Choices(
        ('PRESENTED', 'presented', _('presented')),
        ('COUNCIL', 'council', _('council')),
        ('APPROVED', 'approved', _('approved')),
        ('REJECTED', 'rejected', _('rejected'))
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
    STATUS = Choices(
        ('PRESENTED', 'presented', _('presented')),
        ('COUNCIL', 'council', _('council')),
        ('APPROVED', 'approved', _('approved')),
        ('REJECTED', 'rejected', _('rejected'))
    )

    status = StatusField()

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
    STATUS = Choices(('PRESENTED', 'presented', _('presented')), ('APPROVED', 'approved', _('approved')))
    
    status = StatusField()
    act = models.ForeignKey(Act, related_name='related_emendation_set', on_delete=models.PROTECT)
    act_section = models.ForeignKey(ActSection, null=True, blank=True, on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('emendation')
        verbose_name_plural = _('emendations')



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
    
    Document's content can be specified either as:
    
    * a text string
    * an URL to its textual representation
    * an URL to an external PDF file
    * an uploaded internal PDF file
    
    It is possible for a single document to have more than one type of content:
    for example, a textual and a PDF local versions, or remote links...
    """
    document_date = models.DateField(null=True, blank=True)
    text = models.TextField(blank=True)
    text_url = models.URLField(blank=True)
    pdf_url = models.URLField(blank=True)
    pdf_file = models.FileField(upload_to="attached_documents/%Y%d%m", blank=True)
    
    class Meta:
        abstract = True


class Attach(Document):
    """
    An attachment to a formal act. 

    Extends the ``Document`` class, by adding a title
    and a foreign key to the act the attachment relates to.
    """
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


# TODO: can't find a DRY-way to do it
@receiver(post_save, sender=Deliberation)
def new_deliberation_published(sender, **kwargs):
    new_act_published(sender, **kwargs)

@receiver(post_save, sender=Interrogation)
def new_interrogation_published(sender, **kwargs):
    new_act_published(sender, **kwargs)

def new_act_published(sender, **kwargs):
    """
    generates a record in newscache when an act is presented (inserted in our DB)

    the news is generate only when an act is created, not updated
    and when this happens outside the fixture loading phase

    below, a trick used to handle signals when loading fixtures,
    it is not used now, but it may be useful, for testing purposes
    # instance for subclass fix, while loading fixtures
    # see http://bit.ly/yimn9S and
    # https://code.djangoproject.com/ticket/13299
    if kwargs.get('raw', False):
        instance = kwargs['instance']
        generating_item = instance.__class__._default_manager.get(pk=instance.pk)
    else:
        generating_item = kwargs['instance']
    """

    # generates news only if not in raw mode (fixtures)
    # and for objects creation
    if not kwargs.get('raw', False) and kwargs.get('created', False):
        generating_item = kwargs['instance']

        # create transition: act is presented
        generating_item.transition_set.create(
            act=generating_item.act_ptr,
            final_status=generating_item.STATUS.presented,
            transition_date=generating_item.presentation_date,
            )

        # define context for textual representation of the news
        ctx = Context({  })

        # generate news in newscache
        News.objects.create(
            generating_object=generating_item, related_object=generating_item, priority=1,
            text=News.get_text_for_news(ctx, 'newscache/act_published.html')
        )


@receiver(post_save, sender=ActSupport)
def new_signature(**kwargs):
    """
    generates a record in newscache, when an act is signed
    """
    # generates news only if not in raw mode (fixtures)
    # and for objects creation
    if not kwargs.get('raw', False) and kwargs.get('created', False):
        generating_item = kwargs['instance']
        act = generating_item.act
        signer = generating_item.charge
        # define context for textual representation of the news
        ctx = Context({ 'current_site': Site.objects.get(id=settings.SITE_ID),
                        'signature': generating_item, 'act': act, 'signer': signer })
        News.objects.create(
            generating_object=generating_item, related_object=act, priority=3,
            text=News.get_text_for_news(ctx, 'newscache/act_signed.html')
        )
        News.objects.create(
            generating_object=generating_item, related_object=signer, priority=1,
            text=News.get_text_for_news(ctx, 'newscache/user_signed.html')
        )

@receiver(post_save, sender=Transition)
def new_transition(**kwargs):
    if not kwargs.get('raw', False) and kwargs.get('created', False):
        generating_item = kwargs['instance']
        act = generating_item.act.downcast()

        # Presentation is already handled by new_act_published handler
        if generating_item.final_status != 'PRESENTED':
            # set act's status according to transition status
            act.status = generating_item.final_status
            if act.is_final_status(generating_item.final_status):
                act.status_is_final = True

            act.save()

            # generate news
            ctx = Context({ 'current_site': Site.objects.get(id=settings.SITE_ID),
                            'transition': generating_item, 'act': act })
            News.objects.create(
                generating_object=generating_item, related_object=act, priority=2,
                text=News.get_text_for_news(ctx, 'newscache/act_changed_status.html')
            )

@receiver(post_delete, sender=Transition)
def delete_transition(**kwargs):
    if not kwargs.get('raw', False):
        deleting_item = kwargs['instance']
        act = deleting_item.act.downcast()

        act.status = act.get_last_transition().final_status
        if act.is_final_status(deleting_item.final_status):
            act.status_is_final = False

        act.save()
