from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

from model_utils import Choices
from model_utils.models import TimeStampedModel, StatusModel, TimeFramedModel
from model_utils.managers import InheritanceManager

from south.modelsinspector import add_introspection_rules



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
    process_step_set = models.ManyToManyField('Status', through='Transition', verbose_name=_('transitions'))
    presenter_set = models.ManyToManyField('InstitutionCharge', blank=True, null=True, db_table='om_act_presenter', related_name='act_presentation_set', verbose_name=_('presenters'))
    recipient_set = models.ManyToManyField('InstitutionCharge', blank=True, null=True, db_table='om_act_recipient', related_name='act_destination_set', verbose_name=_('recipients'))
    emitting_institution = models.ForeignKey('Institution', related_name='emitted_act_set', verbose_name=_('emitting institution'))

    objects = InheritanceManager()

    def __unicode__(self):
        uc = u'%s' % (self.title)
        if self.idnum:
            uc = u'%s - %s' % (self.idnum, uc)
        if self.adj_title:
            uc = u'%s (%s)' % (uc, self.adj_title)
        return uc

    @property
    def transitions(self):
        return self.process_step_set.all()

    @property
    def presenters(self):
        return self.presenter_set.all()

    @property
    def recipients(self):
        return self.recipient_set.all()

      
class ActSection(models.Model):
    act = models.ForeignKey('Act', on_delete=models.PROTECT)
    parent_section = models.ForeignKey('ActSection', on_delete=models.PROTECT)  
    title = models.CharField(max_length=128, blank=True)
    text = models.TextField(blank=True)
  
    def __unicode__(self):
        return u'%s' % self.title

    class Meta:
        db_table = u'om_act_section'


class Deliberation(Act):
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

    class Meta:
        verbose_name = _('deliberation')
        verbose_name_plural = _('deliberations')


class Interrogation(Act):
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
    """WRITEME"""
    class Meta:
        verbose_name = _('motion')
        verbose_name_plural = _('motions')


class Agenda(Act):
    """WRITEME"""
    class Meta:
        verbose_name = _('agenda')
        verbose_name_plural = _('agendas')


class Emendation(Act):
    """
    An emendation relates to an act, and it can relate theoretically to another emendation (sub-emendations).
    
    Optionally, an emendation relates to an act section (article, paragraph).
    """
    act = models.ForeignKey('Act', related_name='related_emendation_set', on_delete=models.PROTECT)
    act_section = models.ForeignKey('ActSection', null=True, blank=True, on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('emendation')
        verbose_name_plural = _('emendations')



#
# Processes
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
    transition_date = models.DateField()
    symbol = models.CharField(_('symbol'), max_length=128, null=True)
    note = models.CharField(_('note'), max_length=255, null=True)
    
    class Meta:
        db_table = u'om_transition'
        verbose_name = _('status transition')
        verbose_name_plural = _('status transition')
    


#
# Persons, charges and groups
#
class Person(models.Model):
    FEMALE_SEX = 0
    MALE_SEX = 1
    SEX = Choices(
        (MALE_SEX, _('Male')),    
        (FEMALE_SEX, _('Female')),
        )
    first_name = models.CharField(_('first name'), max_length=128)
    last_name = models.CharField(_('last name'), max_length=128)
    birth_date = models.DateField(_('birth date'))
    birth_location = models.CharField(_('birth location'), blank=True, max_length=128)
    slug = models.SlugField(unique=True, blank=True, null=True, max_length=128)
    sex = models.IntegerField(_('sex'), choices=SEX)
    op_politician_id = models.IntegerField(_('openpolis politician ID'), blank=True, null=True)
    
    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)

    def get_absolute_url(self):
        # FIXME: ``get_absolute_url`` shouldn't contain hard-coded URLs
        return "/persone/%s.html" % self.slug

    class Meta:
        verbose_name = _('person')
        verbose_name_plural = _('persons')


class Charge(models.Model):
    """
    This is the base class for the different macro-types of charges (institution, organization, administration).
    
    Inheritance here is done through abstract classes, since there is no apparent need to browse all.
    """
    person = models.ForeignKey('Person', verbose_name=_('person'))
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'), blank=True, null=True)
    end_reason = models.CharField(_('end reason'), blank=True, max_length=255)
    description = models.CharField(_('description'), blank=True, max_length=255, help_text=_('Insert the complete description of the charge, if it gives more information than the charge type'))

    class Meta:
        abstract = True
    

class InstitutionCharge(Charge):
    """
    This is a charge in the institution (city council, city government, mayor).
    """
    MAYOR_CHARGE = 1
    ASSESSOR_CHARGE = 2
    COUNSELOR_CHARGE = 3
    COUNCIL_PRES_CHARGE = 4
    COUNCIL_VICE_CHARGE = 5
    COMMITTEE_MEMBER_CHARGE = 6
    CHARGE_TYPES = Choices(
      (MAYOR_CHARGE, _('Mayor')),    
      (ASSESSOR_CHARGE, _('Town government member')),
      (COUNCIL_PRES_CHARGE, _('Counsil president')),
      (COUNCIL_VICE_CHARGE, _('Counsil vice president')),
      (COUNSELOR_CHARGE, _('Counselor')),    
      (COMMITTEE_MEMBER_CHARGE, _('Committee member')),
    )
    substitutes = models.OneToOneField('InstitutionCharge', blank=True, null=True, 
                     related_name='reverse_substitute_set', 
                     on_delete=models.PROTECT, 
                     verbose_name=_('in substitution of'))
    substituted_by = models.OneToOneField('InstitutionCharge', blank=True, null=True,
                     related_name='reverse_substituted_by_set', 
                     on_delete=models.PROTECT, 
                     verbose_name=_('substituted by'))
    institution = models.ForeignKey('Institution', on_delete=models.PROTECT, verbose_name=_('institution'))
    charge_type = models.IntegerField(_('charge type'), choices=CHARGE_TYPES)
    op_charge_id = models.IntegerField(_('openpolis institution charge ID'), blank=True, null=True)
    
    def __unicode__(self):
        # TODO: implement ``get_charge_type_display()`` method
        return u'%s - %s' % (self.get_charge_type_display(), self.institution.name)
    
    class Meta(Charge.Meta):
        db_table = u'om_institution_charge'
        verbose_name = _('institution charge')
        verbose_name_plural = _('institution charges')


class CompanyCharge(Charge):
    """
    This is a charge in a company controlled by the municipality (it: partecipate).
    """  
    CEO_CHARGE = 1
    PRES_CHARGE = 2
    VICE_CHARGE = 3
    DIR_CHARGE = 4
    CHARGE_TYPES = Choices(
        (CEO_CHARGE, _('Chief Executive Officer')),
        (PRES_CHARGE, _('President')),    
        (VICE_CHARGE, _('Vice president')),
        (DIR_CHARGE, _('Member of the board')),
    )

    company = models.ForeignKey('Company', on_delete=models.PROTECT, verbose_name=_('company'))
    charge_type = models.IntegerField(_('charge type'), choices=CHARGE_TYPES)
    
    def __unicode__(self):
        # TODO: implement ``get_charge_type_display()`` method
        return u'%s - %s' % (self.get_charge_type_display(), self.company.name)
    
    class Meta(Charge.Meta):
        db_table = u'om_organization_charge'
        verbose_name = _('organization charge')
        verbose_name_plural = _('organization charges')


class AdministrationCharge(Charge):
    """
    This is a charge in the internal municipality administration.
    """
    DIR_CHARGE = 1
    EXEC_CHARGE = 2
    CHARGE_TYPES = Choices(
      (DIR_CHARGE, _('Director')),    
      (EXEC_CHARGE, _('Executive')),
    )

    office = models.ForeignKey('Office', on_delete=models.PROTECT, verbose_name=_('office'))
    charge_type = models.IntegerField(_('charge type'), choices=CHARGE_TYPES)
    
    def __unicode__(self):
        # TODO: implement ``get_charge_type_display()`` method
        return u'%s - %s' % (self.get_charge_type_display(), self.office.name)
    
    class Meta(Charge.Meta):
        db_table = u'om_administration_charge'
        verbose_name = _('administration charge')
        verbose_name_plural = _('administration charges')

  
class Group(models.Model):
    """
    This model represents a group of counselors.
    """
    name = models.CharField(max_length=100)
    acronym = models.CharField(blank=True, max_length=16)
    counselor_set = models.ManyToManyField('InstitutionCharge', through='GroupCharge')

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.acronym)
    
    class Meta:
        verbose_name = _('group')
        verbose_name_plural = _('groups')
        
    @property
    def counselors(self):
        return self.counselor_set.all()
    
    @property
    def majority_records(self):
        return self.groupismajority_set.all()
        
    def is_majority_now(self):
        current_is_maj = self.groupismajority_set.filter(end_date__isnull=True)
        return current_is_maj[0]
    is_majority_now.short_description = _('Is Majority?')
        


class GroupCharge(models.Model):
    """
    This model records the historical composition of council groups. 
    
    This is only valid for ``InstitutionCharges``.
    """
    group = models.ForeignKey('Group')
    charge = models.ForeignKey('InstitutionCharge')
    charge_description = models.CharField(blank=True, max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    end_reason = models.CharField(blank=True, max_length=255)
    
    class Meta:
        db_table = u'om_group_charge'
        verbose_name = _('group charge')
        verbose_name_plural = _('group charges')

class GroupIsMajority(models.Model):
    """
    This model records the historical composition of the majority
    """
    group = models.ForeignKey('Group')
    is_majority = models.BooleanField(_('Is majority'), default=False)
    start_date = models.DateField(_('Start date'))
    end_date = models.DateField(_('End date'), blank=True, null=True)

    def __unicode__(self):
        if self.is_majority:
            return u'yes'
        elif self.is_majority is False:
            return u'no'
        else:
            return u'na'
            
    class Meta:
        verbose_name = _('group majority')
        verbose_name_plural = _('group majorities')


#
# Bodies
#
class Body(models.Model):
    """
    The base model for bodies. 
    
    Uses the *abstract base class* inheritance model.
    """
    name = models.CharField(_('name'), max_length=255)
    slug = models.SlugField(unique=True, blank=True, null=True, help_text=_('Suggested value automatically generated from name, must be unique'))
    description = models.TextField(_('description'), blank=True)
    
    def __unicode__(self):
        return u'%s' % (self.name,)
    
    class Meta:
        abstract = True

  
class Institution(Body):
    """
    Institutional bodies can be of different types (as specified by the ``institution_type`` field).
    
    This model has a relation with itself, in order to map hierarchical bodies (joint committees, ...).
    """
    MAYOR = 1
    TOWN_GOVERNMENT = 2
    COUNCIL = 3
    COMMITTEE = 4
    JOINT_COMMITTEE = 5
    INSTITUTION_TYPES = Choices(
      (MAYOR, _('Mayor')),    
      (COUNCIL, _('Council')),
      (TOWN_GOVERNMENT, _('Town government')),
      (COMMITTEE, _('Committee')),
      (JOINT_COMMITTEE, _('Joint committee')),
    )
    
    parent = models.ForeignKey('Institution', related_name='sub_body_set', blank=True, null=True)
    institution_type = models.IntegerField(choices=INSTITUTION_TYPES)
    
    def get_absolute_url(self):
        # FIXME: ``get_absolute_url`` shouldn't contain hard-coded URLs
        return "/istituzioni/%s.html" % self.slug

    def save(self, *args, **kwargs):
        """slugify name on first save"""
        if not self.id:
            self.slug = slugify(self.name)
        super(Institution, self).save(*args, **kwargs)

    class Meta(Body.Meta):
        verbose_name = _('institution')
        verbose_name_plural = _('institutions')


class Company(Body):
    """
    A company owned by the municipality, whose executives are nominated politically.
    """
    
    def get_absolute_url(self):
        return "/aziende/%s.html" % self.slug
    
    class Meta(Body.Meta):
        verbose_name = _('company')
        verbose_name_plural = _('companies')

  
class Office(Body):
    """
    Internal municipality office, playing a role in municipality's administration.
    """
    def get_abolute_url(self):
        # FIXME: ``get_absolute_url`` shouldn't contain hard-coded URLs
        return "/uffici/%s.html" % self.slug
    
    class Meta(Body.Meta):
        verbose_name = _('office')
        verbose_name_plural = _('offices')

  
#
# Documents
#
class Document(TimeStampedModel):
    """
    An abstract base class for all complex documents. 
    
    Document's content can be specified either as:
    
    * a text string
    * an URL to its textual representation
    * a PDF file (uploaded into a dedicated folder)
    * an URL to a PDF file
    """
    document_date = models.DateField(null=True, blank=True)
    text = models.TextField(blank=True)
    text_url = models.URLField(blank=True)
    pdf_url = models.URLField(blank=True)
    
    class Meta:
        abstract = True


class Attach(Document):
    """
    WRITEME
    """
    title = models.CharField(max_length=255)
    act = models.ForeignKey('Act')
    pdf_file = models.FileField(upload_to="attached_documents/%Y%d%m", blank=True)
    
    def __unicode__(self):
        return u'%s' % self.title
    
    class Meta(Document.Meta):
        verbose_name = _('attach')
        verbose_name_plural = _('attaches')


class Minute(Document):
    """
    WRITEME
    """
    sitting = models.ForeignKey('Sitting')
    act_set = models.ManyToManyField('Act')    
    pdf_file = models.FileField(upload_to="minutes/%Y%d%m", blank=True)
    
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
    sitting = models.ForeignKey('Sitting')
    act_set = models.ManyToManyField('Act')    
    pdf_file = models.FileField(upload_to="outcomes/%Y%d%m", blank=True)

    class Meta(Document.Meta):
        verbose_name = _('outcome')
        verbose_name_plural = _('outcomes')

    @property
    def acts(self):
        return self.act_set.all()
    

class Decision(models.Model):
    """
    WRITEME
    """
    office = models.ForeignKey('Office')
    act_set = models.ManyToManyField('Act')    
    pdf_file = models.FileField(upload_to="decisions/%Y%d%m", blank=True)
    
    class Meta(Document.Meta):
        verbose_name = _('decision')
        verbose_name_plural = _('decisions')

    @property
    def acts(self):
        return self.act_set.all()
    
#
# Sittings
#
class Sitting(models.Model):
    """
    WRITEME
    """
    idnum = models.CharField(blank=True, max_length=64)
    date = models.DateField()
    institution = models.ForeignKey('Institution', on_delete=models.PROTECT)
    
    class Meta:
        verbose_name = _('sitting')
        verbose_name_plural = _('sittings')


#
# Votations
#
class Votation(models.Model):
    """
    WRITEME
    """
    REJECTED = 0
    PASSED = 1
    OUTCOMES = Choices(
      (PASSED, _('Passed')),    
      (REJECTED, _('Rejected')),
    )
    
    idnum = models.CharField(blank=True, max_length=64)
    sitting = models.ForeignKey('Sitting')
    act_set = models.ManyToManyField('Act')
    group_vote_set = models.ManyToManyField('Group', through='GroupVote')
    charge_vote_set = models.ManyToManyField('InstitutionCharge', through='ChargeVote')
    n_legal = models.IntegerField(blank=True, null=True)
    n_presents = models.IntegerField(blank=True, null=True)
    n_yes = models.IntegerField(blank=True, null=True)
    n_no = models.IntegerField(blank=True, null=True)
    n_abst = models.IntegerField(blank=True, null=True)
    n_maj = models.IntegerField(blank=True, null=True)
    outcome = models.IntegerField(choices=OUTCOMES)

    class Meta:
        verbose_name = _('votation')
        verbose_name_plural = _('votations')

    @property
    def acts(self):
        return self.act_set.all()
  
    @property
    def group_votes(self):
        return self.group_vote_set.all()
    
    @property
    def charge_votes(self):
        return self.charge_vote_set.all()


class GroupVote(TimeStampedModel):
    """
    WRITEME
    """
    NO = 0
    YES = 1
    ABSTAINED = 2
    NON_COMPUTABLE = 3
    VOTES = Choices(
      (YES, _('Yes')),    
      (NO, _('No')),
      (ABSTAINED, _('Abstained')),
      (NON_COMPUTABLE, _('Non computable')),
    )
    
    votation = models.ForeignKey('Votation')
    vote = models.IntegerField(choices=VOTES)
    group = models.ForeignKey('Group')

    class Meta:
        db_table = u'om_group_vote'    
        verbose_name = _('group vote')
        verbose_name_plural = _('group votes')


class ChargeVote(TimeStampedModel):
    """
    WRITEME
    """  
    NO = 0
    YES = 1
    ABSTAINED = 2
    MISSION = 3
    ABSENT = 4
    INVALID = 5
    PRES = 6
    REQUIRES = 7
    CANCELED = 8
    SECRET = 9
    VOTES = Choices(
    (YES, _('Yes')),    
    (NO, _('No')),
    (ABSTAINED, _('Abstained')),
    (MISSION, _('Is on mission')),
    (ABSENT, _('Is absent')),
    (INVALID, _('Participates to an invalid votation')),
    (PRES, _('President during votation')),
    (REQUIRES, _('Requires votation, but does not vote')),
    (CANCELED, _('Canceled votation')),
    (SECRET, _('Secret votation')),
    )

    votation = models.ForeignKey('Votation')
    vote = models.IntegerField(choices=VOTES)
    charge = models.ForeignKey('InstitutionCharge')
    rebel = models.BooleanField(default=False)

    class Meta:
        db_table = u'om_charge_vote'    
        verbose_name = _('charge vote')
        verbose_name_plural = _('charge votes')