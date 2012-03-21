# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.template.context import Context
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from django.db.models.signals import post_save
from django.dispatch import receiver

from model_utils import Choices
from model_utils.managers import InheritanceManager
from model_utils.models import TimeStampedModel
from model_utils.fields import StatusField

from taggit.managers import TaggableManager
from open_municipio.newscache.models import News

from open_municipio.people.models import Institution, InstitutionCharge, Sitting
from open_municipio.taxonomy.models import TaggedAct, Category, Location
from open_municipio.monitoring.models import Monitoring



#
# Acts
#

class Act(TimeStampedModel):
    """
    This is the base class for all the different act types: it contains the common fields for
    deliberations, interrogations, interpellations, motions, agendas and emendations.
  
    It is a ``TimeStampedModel``, so it tracks creation and modification timestamps for each record.

    The ``related_news`` attribute can be used  to fetch
    news related to it (or its subclasses) from ``newscache.News``

    Inheritance is done through multi-table inheritance, since browsing the whole set of acts may be useful.
    The default manager is the ``InheritanceManager`` (from package ``django-model-utils``_),
    that enables the ``select_subclasses()`` method, allowing the retrieval of subclasses, when needed.


    .. _django-model-utils: https://bitbucket.org/carljm/django-model-utils/src

    """

    idnum = models.CharField(max_length=64, blank=True, help_text=_("A string representing the identification number or sequence, used internally by the administration."))
    title = models.CharField(_('title'), max_length=255, blank=True)
    adj_title = models.CharField(_('adjoint title'), max_length=255, blank=True, help_text=_("An adjoint title, added to further explain an otherwise cryptic title"))
    presentation_date = models.DateField(_('presentation date'), null=True, help_text=_("Date of presentation, as stated in the act"))
    text = models.TextField(_('text'), blank=True)
    presenter_set = models.ManyToManyField(InstitutionCharge, blank=True, null=True, through='ActSupport', related_name='presenter_act_set', verbose_name=_('presenters'))
    recipient_set = models.ManyToManyField(InstitutionCharge, blank=True, null=True, related_name='recipient_act_set', verbose_name=_('recipients'))
    emitting_institution = models.ForeignKey(Institution, related_name='emitted_act_set', verbose_name=_('emitting institution'))
    category_set = models.ManyToManyField(Category, verbose_name=_('categories'), blank=True, null=True)
    location_set = models.ManyToManyField(Location, verbose_name=_('locations'), blank=True, null=True)
    status_is_final = models.BooleanField(default=False)

    objects = InheritanceManager()
    
    tag_set = TaggableManager(through=TaggedAct, blank=True)


    # manager to handle the list of news that have the act as related object
    related_news_set = generic.GenericRelation(News,
                                               content_type_field='related_content_type',
                                               object_id_field='related_object_pk')


    # manager to handle the list of monitoring having as content_object this instance
    monitoring_set = generic.GenericRelation(Monitoring, object_id_field='object_pk')
    
    def __unicode__(self):
        uc = u'%s' % (self.title, )
        if self.idnum:
            uc = u'%s - %s' % (self.idnum, uc)
        if self.adj_title:
            uc = u'%s (%s)' % (uc, self.adj_title)
        return uc
   
    @models.permalink
    def get_absolute_url(self):
        return 'om_act_detail', (), {'pk': str(self.pk)}
    
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
    def tags(self):
        return self.tag_set.all()
    
    @property
    def categories(self):
        return self.category_set.all()
    
    @property
    def locations(self):
        return self.location_set.all()
    
    @property
    def monitorings(self):
        """
        Returns the monitorings associated with this act (as a QuerySet).
        """
        return self.monitoring_set.all()
    
    @property
    def monitoring_users(self):
        """
        Returns the list of users monitoring this act.
        """
        return [m.user for m in self.monitorings]
        
    @property
    def content_type_id(self):
        """
        Returns id of the content type associated with this instance.
        """
        return ContentType.objects.get_for_model(self).id

    def status(self):
        """
        Returns the current status for the downcasted version of this act instance. 
        """
        return self.downcast().status

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

      
class ActSection(models.Model):
    """
    WRITEME
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
    WRITEME
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


class Agenda(Act):
    """
    Maps the *Ordine del Giorno* act type.
    It is a political act, used to publicly influence the following discussions on Deliberations.
    It is specifically used with respect to issues specific to the deliberation process.
    It is submitted to the Council approval and Emendations to it can be presented before the votation.
    """
    # TODO: add additional statuses allowed for this act type
    STATUS = Choices(('PRESENTED', 'presented', _('presented')), ('APPROVED', 'approved', _('approved')))

    status = StatusField()
    
    class Meta:
        verbose_name = _('agenda')
        verbose_name_plural = _('agenda')

    @models.permalink
    def get_absolute_url(self):
        return ('om_agenda_detail', (), {'pk': str(self.pk)})
    
    
class Deliberation(Act):
    """
    WRITEME
    """
    COUNSELOR_INIT = 1
    PRESIDENT_INIT = 2
    ASSESSOR_INIT = 3
    GOVERNMENT_INIT = 4
    MAYOR_INIT = 5
    INIZIATIVE_CHOICES = (
        (COUNSELOR_INIT, _('Counselor')),
        (PRESIDENT_INIT, _('President')),
        (ASSESSOR_INIT, _('City Government Member')),
        (GOVERNMENT_INIT, _('City Government')),
        (MAYOR_INIT, _('Mayor')),
    )
    # TODO: add additional statuses allowed for this act type
    STATUS = Choices(
        ('PRESENTED', 'presented', _('presented')),
        ('COMMISSION', 'commission', _('commission')),
        ('COUNCIL', 'council', _('council')),
        ('APPROVED', 'approved', _('approved')),
        ('REJECTED', 'rejected', _('rejected'))
    )
    
    status = StatusField()
    approval_date = models.DateField(_('approval date'), null=True, blank=True)
    publication_date = models.DateField(_('publication date'), null=True, blank=True)
    execution_date = models.DateField(_('execution date'), null=True, blank=True)
    initiative = models.IntegerField(_('initiative'), choices=INIZIATIVE_CHOICES)
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
    WRITTEN_ANSWER = 1
    VERBAL_ANSWER = 2
    ANSWER_TYPES = Choices(
        (WRITTEN_ANSWER, _('Written')),
        (VERBAL_ANSWER, _('Verbal')),
    )
    # TODO: add additional statuses allowed for this act type
    STATUS = Choices(('PRESENTED', 'presented', _('presented')), ('ANSWERED', 'answered', _('answered')))
    
    status = StatusField()
    answer_type = models.IntegerField(_('answer type'), choices=ANSWER_TYPES)
    question_motivation = models.TextField(blank=True)
    answer_text = models.TextField(blank=True)
    reply_text = models.TextField(blank=True)

    class Meta:
        verbose_name = _('interrogation')
        verbose_name_plural = _('interrogations')
    
    @models.permalink
    def get_absolute_url(self):
        return ('om_interrogation_detail', (), {'pk': str(self.pk)})
    

class Interpellation(Act):
    """
    WRITEME
    """
    WRITTEN_ANSWER = 1
    VERBAL_ANSWER = 2
    ANSWER_TYPES = Choices(
        (WRITTEN_ANSWER, _('Written')),
        (VERBAL_ANSWER, _('Verbal')),
    )
    # TODO: add additional statuses allowed for this act type
    STATUS = Choices(('PRESENTED', 'presented', _('presented')), ('ANSWERED', 'answered', _('answered')))
    
    status = StatusField()
    answer_type = models.IntegerField(_('answer type'), choices=ANSWER_TYPES)
    question_motivation = models.TextField(blank=True)
    answer_text = models.TextField(blank=True)

    class Meta:
        verbose_name = _('interpellation')
        verbose_name_plural = _('interpellations')
    
    @models.permalink
    def get_absolute_url(self):
        return ('om_interpellation_detail', (), {'pk': str(self.pk)})
    

class Motion(Act):
    """
    It is a political act, used to publicly influence members of the City Government, or the Mayor,
    on a broad type of issues (specific to the Comune proceedings, or of a more general category)
    It is submitted to the Council approval and Emendations to it can be presented before the votation.
    """
    # TODO: add additional statuses allowed for this act type
    STATUS = Choices(('PRESENTED', 'presented', _('presented')), ('APPROVED', 'approved', _('approved')))
    
    status = StatusField()
    
    class Meta:
        verbose_name = _('motion')
        verbose_name_plural = _('motions')
        
    @models.permalink
    def get_absolute_url(self):
        return ('om_motion_detail', (), {'pk': str(self.pk)})
    


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
        act = generating_item.act

        # Presentation is already handled by new_act_published handler
        if generating_item.final_status != act.STATUS.presented:
            # set act's status according to transition status
            act.status = generating_item.final_status
            act.save()

            # generate news
            ctx = Context({ 'current_site': Site.objects.get(id=settings.SITE_ID),
                            'transition': generating_item, 'act': act })
            News.objects.create(
                generating_object=generating_item, related_object=act, priority=2,
                text=News.get_text_for_news(ctx, 'newscache/act_changed_status.html')
            )
