from django.db import models
from django.utils.translation import ugettext_lazy as _

from model_utils import Choices
from model_utils.managers import InheritanceManager
from model_utils.models import TimeStampedModel 

from taggit.managers import TaggableManager

from open_municipio.people.models import Institution, InstitutionCharge, Sitting
from open_municipio.taxonomy.models import TaggedItem, Category

#
# Acts
#

class Act(TimeStampedModel):
    """
    This is the base class for all the different act types: it contains the common fields for
    deliberations, interrogations, interpellations, motions, agendas and emendations.
  
    It is a ``TimeStampedModel``, so it tracks creation and modification timestamps for each record.
   
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
    transitions = models.ManyToManyField('Status', blank=True, null=True, through='Transition', verbose_name=_('transitions'))
    presenters = models.ManyToManyField(InstitutionCharge, blank=True, null=True, through='ActSupport', related_name='presenter_act_set', verbose_name=_('presenters'))
    recipients = models.ManyToManyField(InstitutionCharge, blank=True, null=True, db_table='acts_act_recipient', related_name='recipient_act_set', verbose_name=_('recipients'))
    emitting_institution = models.ForeignKey(Institution, related_name='emitted_act_set', verbose_name=_('emitting institution'))
    category_set = models.ManyToManyField(Category, verbose_name=_('categories'), blank=True, null=True)

    objects = InheritanceManager()
    
    tag_set = TaggableManager(through=TaggedItem, blank=True)

    def __unicode__(self):
        uc = u'%s' % (self.title)
        if self.idnum:
            uc = u'%s - %s' % (self.idnum, uc)
        if self.adj_title:
            uc = u'%s (%s)' % (uc, self.adj_title)
        return uc
   
    @models.permalink
    def get_absolute_url(self):
        return ('om_act_detail', (), {'pk': str(self.pk)})
    
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
    FIRST_SIGNER = 1
    CO_SIGNER = 2
    RELATOR = 3
    SUPPORT_TYPE_CHOICES = (
        (FIRST_SIGNER, _('First signer')),
        (CO_SIGNER, _('Co signer')),
        (RELATOR, _('Relator')),
    )
    charge = models.ForeignKey(InstitutionCharge)
    act = models.ForeignKey(Act)
    support_type = models.IntegerField(_('support type'), choices=SUPPORT_TYPE_CHOICES)    
    support_date = models.DateField(_('support date'), default=None, blank=True, null=True)

    class Meta:
        db_table = u'acts_act_support'
    
    
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

    approval_date = models.DateField(_('approval date'), null=True, blank=True)
    publication_date = models.DateField(_('publication date'), null=True, blank=True)
    execution_date = models.DateField(_('execution date'), null=True, blank=True)
    initiative = models.IntegerField(_('initiative'), choices=INIZIATIVE_CHOICES)
    approved_text = models.TextField(blank=True)
    
    class Meta:
        verbose_name = _('deliberation')
        verbose_name_plural = _('deliberations')


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
  
    answer_type = models.IntegerField(_('answer type'), choices=ANSWER_TYPES)
    question_motivation = models.TextField(blank=True)
    answer_text = models.TextField(blank=True)
    reply_text = models.TextField(blank=True)

    class Meta:
        verbose_name = _('interrogation')
        verbose_name_plural = _('interrogations')


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
    
    answer_type = models.IntegerField(_('answer type'), choices=ANSWER_TYPES)
    question_motivation = models.TextField(blank=True)
    answer_text = models.TextField(blank=True)

    class Meta:
        verbose_name = _('interpellation')
        verbose_name_plural = _('interpellations')


class Motion(Act):
    """
    WRITEME
    """
    class Meta:
        verbose_name = _('motion')
        verbose_name_plural = _('motions')



class Emendation(Act):
    """
    An emendation relates to an act, and it can relate theoretically to another emendation (sub-emendations).
    
    Optionally, an emendation relates to an act section (article, paragraph).
    """
    act = models.ForeignKey(Act, related_name='related_emendation_set', on_delete=models.PROTECT)
    act_section = models.ForeignKey(ActSection, null=True, blank=True, on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('emendation')
        verbose_name_plural = _('emendations')



#
# Workflows
#

class Status(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField()
  
    def __unicode__(self):
        return u'%s' % self.name
    
    class Meta:
        verbose_name = _('status')
        verbose_name_plural = _('statuses')
  
  
class Transition(models.Model):
    final_status = models.ForeignKey(Status, on_delete=models.PROTECT)
    act = models.ForeignKey(Act)
    sitting = models.ForeignKey(Sitting, null=True, blank=True, on_delete=models.PROTECT)
    transition_date = models.DateField(default=None)
    symbol = models.CharField(_('symbol'), max_length=128, null=True)
    note = models.CharField(_('note'), max_length=255, null=True)
    
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
    for example, a textual and a pdf local versions, or remote links ...
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
    
    def __unicode__(self):
        return u'%s' % self.title
    
    class Meta(Document.Meta):
        verbose_name = _('attach')
        verbose_name_plural = _('attaches')


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

