from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices
from model_utils.models import TimeStampedModel, StatusModel, TimeFramedModel
from model_utils.managers import InheritanceManager
from tagging.fields import TagField

from south.modelsinspector import add_introspection_rules

add_introspection_rules([], ["^tagging\.fields\.TagField"])


# 
# Acts
#
class Act(TimeStampedModel):
  '''
  This is the base class for all the different act types: it contains the common fields for
  deliberations, interrogations, interpellations, motions, agendas and emendations
  
  It is a TimeStampedModel, so it tracks creation and modification timestamps for each record.
  
  Inheritance is done through multi-table inheritance, since browsing the whole set of acts may be useful.
  The default Manager is the model_utils.managers.InheritanceManager (https://bitbucket.org/carljm/django-model-utils/src),
  that enables the select_subclasses() method, allowing the retrieval of subclasses, when needed.
  '''
  idnum = models.CharField(max_length=64, blank=True, help_text=_("A string representing the identification number or sequence, used internally by the administration."))
  title = models.CharField(_('title'), max_length=255, blank=True)
  adj_title = models.CharField(_('adjoint title'), max_length=255, blank=True, help_text=_("An adjoint title, added to further explain an otherwise cryptic title"))
  presentation_date = models.DateField(_('presentation date'), null=True, help_text=_("Date of presentation, as stated in the act"))
  text = models.TextField(_('text'), blank=True)
  process_steps = models.ManyToManyField('Process', through='ProcessStep', verbose_name=_('process steps'))
  presenters = models.ManyToManyField('InstitutionCharge', blank=True, null=True, db_table='om_act_presenter', related_name='act_presentations', verbose_name=_('presenters'))
  recipients = models.ManyToManyField('InstitutionCharge', blank=True, null=True, db_table='om_act_recipient', related_name='act_destinations', verbose_name=_('recipients'))
  emitting_institution = models.ForeignKey('Institution', related_name='emitted_acts_set', verbose_name=_('emitting institution'))

  tags = TagField()
  objects = InheritanceManager()

  def __unicode__(self):
    uc = u'%s' % (self.title)
    if self.idnum:
      uc = u'%s - %s' % (self.idnum, uc)
    if self.adj_title:
      uc = u'%s (%s)' % (uc, self.adj_title)
    return uc

      
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
  INIZIATIVE_CHOICES = (
      ('cou', _('Counselor')),
      ('pre', _('President')),
      ('cgm', _('City Government Member')),
      ('cgo', _('City Government')),
      ('may', _('Mayor')),
  )
  approval_date = models.DateField(_('approval date'), null=True, blank=True)
  publication_date = models.DateField(_('publication date'), null=True, blank=True)
  execution_date = models.DateField(_('execution date'), null=True, blank=True)
  initiative = models.CharField(_('initiative'), max_length=3, choices=INIZIATIVE_CHOICES)

  class Meta:
    verbose_name = _('deliberation')
    verbose_name_plural = _('deliberations')


class Interrogation(Act):
  ANSWER_TYPES = Choices(
    ('w', _('Written')),
    ('v', _('Verbal')),
  )
  answer_type = models.CharField(max_length=1, choices=ANSWER_TYPES)
  question_motivation = models.TextField(blank=True)
  answer_text = models.TextField(blank=True)
  reply_text = models.TextField(blank=True)

  class Meta:
    verbose_name = _('interrogation')
    verbose_name_plural = _('interrogations')


class Interpellation(Act):
  ANSWER_TYPES = Choices(
    ('w', _('Written')),
    ('v', _('Verbal')),
  )
  answer_type = models.CharField(max_length=3, choices=ANSWER_TYPES)
  question_motivation = models.TextField(blank=True)
  answer_text = models.TextField(blank=True)

  class Meta:
    verbose_name = _('interpellation')
    verbose_name_plural = _('interpellations')


class Motion(Act):
  class Meta:
    verbose_name = _('motion')
    verbose_name_plural = _('motions')

class Agenda(Act):
  class Meta:
    verbose_name = _('agenda')
    verbose_name_plural = _('agendas')

class Emendation(Act):
  '''
  an emendation relates to an act, and it can relate theoretically to another emendation (sub-emendations)
  optionally, an emendation relates to an act section (article, paragraph)
  '''
  act = models.ForeignKey('Act', related_name='related_emendations', on_delete=models.PROTECT)
  act_section = models.ForeignKey('ActSection', null=True, blank=True, on_delete=models.PROTECT)

  class Meta:
    verbose_name = _('emendation')
    verbose_name_plural = _('emendations')



#
# Processes
#
class Process(models.Model):
  name = models.CharField(max_length=128)
  slug = models.SlugField()
  
  def __unicode__(self):
    return u'%s' % self.name
    
  class Meta:
    verbose_name = _('process')
    verbose_name_plural = _('processes')
  
class ProcessStep(models.Model):
  process = models.ForeignKey(Process, on_delete=models.PROTECT)
  act = models.ForeignKey(Act)
  transition_date = models.DateField()

  class Meta:
    db_table = u'om_process_step'
    verbose_name = _('process step')
    verbose_name_plural = _('processes steps')



#
# Persons, charges and groups
#
class Person(models.Model):
  SEX = Choices(
    ('m', _('Male')),    
    ('f', _('Female')),
  )
  first_name = models.CharField(_('first name'), max_length=128)
  last_name = models.CharField(_('last name'), max_length=128)
  birth_date = models.DateField(_('birth date'))
  birth_location = models.CharField(_('birth location'), blank=True, max_length=128)
  sex = models.CharField(_('sex'), max_length=1, choices=SEX)
  op_politician_id = models.IntegerField(_('openpolis politician ID'), blank=True, null=True)
  def __unicode__(self):
    return u'%s %s' % (self.first_name, self.last_name)

  class Meta:
    verbose_name = _('person')
    verbose_name_plural = _('persons')


class Charge(models.Model):
  '''
  This is the base class for the different macro-types of charges (institution, organization, administration).
  Inheritance here is done through Abstract Classes, since there is no apparent need to browse all 
  '''
  person = models.ForeignKey('Person', verbose_name=_('person'))
  start_date = models.DateField(_('start date'))
  end_date = models.DateField(_('end date'), blank=True, null=True)
  end_reason = models.CharField(_('end reason'), blank=True, max_length=255)
  description = models.CharField(_('description'), blank=True, max_length=255, help_text=_('Insert the complete description of the charge, if it gives more information than the charge type'))

  class Meta:
    abstract = True
    

class InstitutionCharge(Charge):
  '''
  this is a charge in the institution (city council, city government, mayor)
  '''
  CHARGE_TYPES = Choices(
    ('may', _('Mayor')),    
    ('tgm', _('Town government member')),
    ('cpr', _('Counsil president')),
    ('cvp', _('Counsil vice president')),
    ('cou', _('Counselor')),    
    ('com', _('Committee member')),
  )
  substitutes = models.OneToOneField('InstitutionCharge', blank=True, null=True, related_name='reverse_substitutes', on_delete=models.PROTECT, verbose_name=_('in substitution of'))
  substituted_by = models.OneToOneField('InstitutionCharge', blank=True, null=True, related_name='reverse_substituted_by', on_delete=models.PROTECT, verbose_name=_('substituted by'))
  institution = models.ForeignKey('Institution', on_delete=models.PROTECT, verbose_name=_('institution'))
  charge_type = models.CharField(_('charge type'), max_length=3, choices=CHARGE_TYPES)
  op_charge_id = models.IntegerField(_('openpolis institution charge ID'), blank=True, null=True)

  def __unicode__(self):
    return u'%s - %s' % (self.get_charge_type_display(), self.institution.name)

  class Meta(Charge.Meta):
    db_table = u'om_institution_charge'
    verbose_name = _('institution charge')
    verbose_name_plural = _('institution charges')

class CompanyCharge(Charge):
  '''
  this is a charge in a company controlled by the municipality (it: partecipate)
  '''  
  CHARGE_TYPES = Choices(
    ('pre', _('President')),    
    ('ceo', _('Chief Executive Officer')),
    ('dir', _('Member of the board')),
  )
  company = models.ForeignKey('Company', on_delete=models.PROTECT, verbose_name=_('company'))
  charge_type = models.CharField(_('charge type'), max_length=3, choices=CHARGE_TYPES)

  def __unicode__(self):
    return u'%s - %s' % (self.get_charge_type_display(), self.company.name)

  class Meta(Charge.Meta):
    db_table = u'om_organization_charge'
    verbose_name = _('organization charge')
    verbose_name_plural = _('organization charges')

class AdministrationCharge(Charge):
  '''
  this is a charge in the internal municipality administration
  '''
  CHARGE_TYPES = Choices(
    ('dir', _('Director')),    
    ('exe', _('Executive')),
  )
  office = models.ForeignKey('Office', on_delete=models.PROTECT, verbose_name=_('office'))
  charge_type = models.CharField(_('charge type'), max_length=3, choices=CHARGE_TYPES)

  def __unicode__(self):
    return u'%s - %s' % (self.get_charge_type_display(), self.office.name)

  class Meta(Charge.Meta):
    db_table = u'om_administration_charge'
    verbose_name = _('administration charge')
    verbose_name_plural = _('administration charges')


  
class Group(models.Model):
  '''
  the class maps the groups of counselors
  '''
  name = models.CharField(max_length=100)
  acronym = models.CharField(blank=True, max_length=16)
  counselors = models.ManyToManyField('InstitutionCharge', through='GroupCharge')

  class Meta:
    verbose_name = _('group')
    verbose_name_plural = _('groups')
  
class GroupCharge(models.Model):
  '''
  maps the historical composition of council groups, this is only valid for InstitutionCharges
  
  '''
  group = models.ForeignKey('Group')
  charge = models.ForeignKey('InstitutionCharge')
  charge_description = models.CharField(blank=True, max_length=255)
  start_date = models.DateField()
  end_date = models.DateField()
  end_reason = models.CharField(blank=True, max_length=255)
  
  class Meta:
    db_table = u'om_group_charge'
    verbose_name = _('group charge')
    verbose_name_plural = _('group charges')


#
# Bodies
#
class Body(models.Model):
  '''
  base class for the body, uses the Abstract Class inheritance model
  '''
  name = models.CharField(_('name'), max_length=255)
  description = models.TextField(_('description'), blank=True)
  def __unicode__(self):
    return u'%s' % (self.name,)

  class Meta:
    abstract = True
  
class Institution(Body):
  '''
  institutional bodies can be of different types and the types are mapped in institution_type
  it has a relation with itself, in order to map hierarchical bodies (joint committee, ...)
  '''
  INSTITUTION_TYPES = Choices(
    ('may', _('Mayor')),    
    ('cou', _('Counsil')),
    ('tgv', _('Town government')),
    ('com', _('Committee')),
    ('jco', _('Joint committee')),
  )
  parent = models.ForeignKey('Institution', related_name='sub_bodies_set', blank=True, null=True)
  institution_type = models.CharField(max_length=3, choices=INSTITUTION_TYPES)

  class Meta(Body.Meta):
    verbose_name = _('institution')
    verbose_name_plural = _('institutions')

class Company(Body):
  '''
  company owned by the municipality, whose executives are nominated politically
  '''
  class Meta(Body.Meta):
    verbose_name = _('company')
    verbose_name_plural = _('companies')
  
class Office(Body):
  '''
  internal municipality office, that plays a role in the administration of the municipalities
  '''
  class Meta(Body.Meta):
    verbose_name = _('office')
    verbose_name_plural = _('offices')

  
#
# Documents
#
class Document(TimeStampedModel):
  '''
  base class for all complex documents, text can be in a text field, in a url, or it can be a pdf,
  uploaded into a dedicated folder, or a url to a pdf
  '''
  document_date = models.DateField(null=True, blank=True)
  text = models.TextField(blank=True)
  text_url = models.URLField(blank=True, verify_exists=True)
  pdf_url = models.URLField(blank=True, verify_exists=True)

  class Meta:
    abstract = True

class Attach(Document):
  title = models.CharField(max_length=255)
  act = models.ForeignKey('Act')
  pdf_file = models.FileField(upload_to="attached_documents/%Y%d%m", blank=True)

  def __unicode__(self):
    return u'%s' % self.title

  class Meta(Document.Meta):
    verbose_name = _('attach')
    verbose_name_plural = _('attaches')


class Minute(Document):
  sitting = models.ForeignKey('Sitting')
  acts = models.ManyToManyField('Act')    
  pdf_file = models.FileField(upload_to="minutes/%Y%d%m", blank=True)

  class Meta(Document.Meta):
    verbose_name = _('minute')
    verbose_name_plural = _('minutes')

class Outcome(models.Model):
  sitting = models.ForeignKey('Sitting')
  acts = models.ManyToManyField('Act')    
  pdf_file = models.FileField(upload_to="outcomes/%Y%d%m", blank=True)

  class Meta(Document.Meta):
    verbose_name = _('outcome')
    verbose_name_plural = _('outcomes')

class Decision(models.Model):
  office = models.ForeignKey('Office')
  acts = models.ManyToManyField('Act')    
  pdf_file = models.FileField(upload_to="decisions/%Y%d%m", blank=True)

  class Meta(Document.Meta):
    verbose_name = _('decision')
    verbose_name_plural = _('decisions')

#
# Sittings
#
class Sitting(models.Model):
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
  OUTCOMES = Choices(
    ('pas', _('Passed')),    
    ('rej', _('Rejected')),
  )
  idnum = models.CharField(blank=True, max_length=64)
  sitting = models.ForeignKey('Sitting')
  acts = models.ManyToManyField('Act')
  group_votes = models.ManyToManyField('Group', through='GroupVote')
  charge_votes = models.ManyToManyField('InstitutionCharge', through='ChargeVote')
  n_legal = models.IntegerField(blank=True, null=True)
  n_presents = models.IntegerField(blank=True, null=True)
  n_yes = models.IntegerField(blank=True, null=True)
  n_no = models.IntegerField(blank=True, null=True)
  n_abst = models.IntegerField(blank=True, null=True)
  n_maj = models.IntegerField(blank=True, null=True)
  outcome = models.CharField(max_length=3, choices=OUTCOMES)

  class Meta:
    verbose_name = _('votation')
    verbose_name_plural = _('votations')

class GroupVote(TimeStampedModel):
  VOTES = Choices(
    ('yes', _('Yes')),    
    ('no', _('No')),
    ('ab', _('Abstained')),
    ('nc', _('Non computable')),
  )
  votation = models.ForeignKey('Votation')
  vote = models.CharField(max_length=3, choices=VOTES)
  group = models.ForeignKey('Group')
  class Meta:
    db_table = u'om_group_vote'    
    verbose_name = _('group vote')
    verbose_name_plural = _('group votes')

class ChargeVote(TimeStampedModel):
  VOTES = Choices(
    ('yes', _('Yes')),    
    ('no', _('No')),
    ('ab', _('Abstained')),
    ('mis', _('Is on mission')),
    ('abs', _('Is absent')),
    ('inv', _('Participates to an invalid votation')),
    ('pre', _('President during votation')),
    ('rnv', _('Requires votation, but does not vote')),
    ('can', _('Canceled votation')),
    ('sec', _('Secret votation')),
  )
  votation = models.ForeignKey('Votation')
  vote = models.CharField(max_length=3, choices=VOTES)
  charge = models.ForeignKey('InstitutionCharge')
  rebel = models.BooleanField(default=False)
  class Meta:
    db_table = u'om_charge_vote'    
    verbose_name = _('charge vote')
    verbose_name_plural = _('charge votes')
    
    