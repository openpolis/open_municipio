from django.db import models
from django.utils.translation import ugettext as _
from model_utils import Choices
from model_utils.models import TimeStampedModel, StatusModel, TimeFramedModel
from model_utils.managers import InheritanceManager
from tagging.fields import TagField

class Act(TimeStampedModel):
  '''
  This is the base class for all the different act types: it contains the common fields for
  deliberations, interrogations, interpellations, motions, agendas and emendations
  
  It is a TimeStampedModel, so it tracks creation and modification timestamps for each record.
  
  Inheritance is done through multi-table inheritance, since browsing the whole set of acts may be useful.
  The default Manager is the model_utils.managers.InheritanceManager (https://bitbucket.org/carljm/django-model-utils/src),
  that enables the select_subclasses() method, allowing the retrieval of subclasses, when needed.
  '''
  idnum = models.CharField(max_length=64, blank=True, help_text="A string representing the identification number or sequence, used internally by the administration.")
  title = models.CharField(max_length=255, blank=True)
  adj_title = models.CharField(max_length=255, blank=True, help_text="An adjoint title, added to further explain an otherwise cryptic title")
  presentation_date = models.DateField(null=True, help_text="Date of publication, as stated in the act")
  text = models.TextField(blank=True)
  process_steps = models.ManyToManyField('Process', through='ProcessStep')
  presenters = models.ManyToManyField('InstitutionCharge', blank=True, null=True, db_table='om_act_presenter', related_name='act_presentations')
  recipients = models.ManyToManyField('InstitutionCharge', blank=True, null=True, db_table='om_act_recipient', related_name='act_destinations')
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
  act = models.ForeignKey('Act')
  parent_section = models.ForeignKey('ActSection')  
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
  approval_date = models.DateField(null=True, blank=True)
  publication_date = models.DateField(null=True, blank=True)
  execution_date = models.DateField(null=True, blank=True)
  initiative = models.CharField(max_length=3, choices=INIZIATIVE_CHOICES)
  minute = models.TextField(blank=True)


class Interrogation(Act):
  ANSWER_TYPES = Choices(
    ('w', _('Written')),
    ('v', _('Verbal')),
  )
  answer_type = models.CharField(max_length=1, choices=ANSWER_TYPES)
  question_motivation = models.TextField(blank=True)
  answer_text = models.TextField(blank=True)
  reply_text = models.TextField(blank=True)


class Interpellation(Act):
  ANSWER_TYPES = Choices(
    ('w', _('Written')),
    ('v', _('Verbal')),
  )
  answer_type = models.CharField(max_length=3, choices=ANSWER_TYPES)
  question_motivation = models.TextField(blank=True)
  answer_text = models.TextField(blank=True)


class Motion(Act):
  pass

class Agenda(Act):
  pass

class Emendation(Act):
  act = models.ForeignKey('Act', related_name="%(app_label)s_%(class)s_related")
  act_section = models.ForeignKey('ActSection', null=True, blank=True)

class AttachedDocument(TimeStampedModel):
  title = models.CharField(max_length=255)
  act = models.ForeignKey('Act')
  document_date = models.DateField(null=True, blank=True)
  text = models.TextField(blank=True)
  text_url = models.CharField(max_length=255, blank=True)
  pdf_file = models.FileField(upload_to="attached_documents/%Y%d%m", blank=True)
  pdf_url = models.CharField(max_length=255, blank=True)

  def __unicode__(self):
    return u'%s' % self.title

  class Meta:
    db_table = u'om_attached_document'


class Process(models.Model):
  name = models.CharField(max_length=128)
  slug = models.CharField(max_length=128)
  
  def __unicode__(self):
    return u'%s' % self.name
    
  class Meta:
    verbose_name_plural = u'Processes'
  
class ProcessStep(models.Model):
  process = models.ForeignKey(Process)
  act = models.ForeignKey(Act)
  transition_date = models.DateField()

  class Meta:
    db_table = u'om_process_step'


class Person(models.Model):
  first_name = models.CharField(max_length=128)
  last_name = models.CharField(max_length=128)
  birth_date = models.DateField()
  birth_location = models.CharField(blank=True, max_length=128)
  op_politician_id = models.IntegerField(blank=True, null=True)
  def __unicode__(self):
    return u'%s %s' % (self.first_name, self.last_name)


class Charge(models.Model):
  '''
  This is the base class for the different macro-types of charges (institution, organization, administration).
  Inheritance here is done through Abstract Classes, since there is no apparent need to browse all 
  '''
  person = models.ForeignKey('Person')
  start_date = models.DateField()
  end_date = models.DateField()
  end_reason = models.CharField(blank=True, max_length=255)

  class Meta:
    abstract = True

class InstitutionCharge(Charge):
  '''
  this is a charge in the institution (city council, city government, mayor)
  '''
  CHARGE_DETAILS = Choices(
    ('may', _('Mayor')),    
    ('cgm', _('City government member')),
    ('cpr', _('Counsil president')),
    ('cvp', _('Counselor')),
    ('com', _('Committee member')),
  )
  substitutes = models.OneToOneField('InstitutionCharge', blank=True, null=True, related_name='reverse_substitutes')
  substituted_by = models.OneToOneField('InstitutionCharge', blank=True, null=True, related_name='reverse_substituted_by')
  institution = models.ForeignKey('Institution')
  charge_detail = models.CharField(max_length=3, choices=CHARGE_DETAILS)
  
  class Meta(Charge.Meta):
    db_table = u'om_institution_charge'

class CompanyCharge(Charge):
  '''
  this is a charge in a company controlled by the municipality (it: partecipate)
  '''  
  CHARGE_DETAILS = Choices(
    ('pre', _('President')),    
    ('ceo', _('Chief Executive Officer')),
    ('dir', _('Member of the board')),
  )
  company = models.ForeignKey('Company')
  charge_detail = models.CharField(max_length=3, choices=CHARGE_DETAILS)
  class Meta(Charge.Meta):
    db_table = u'om_organization_charge'

class AdministrationCharge(Charge):
  '''
  this is a charge in the internal municipality administration
  '''
  CHARGE_DETAILS = Choices(
    ('dir', _('Director')),    
    ('exe', _('Executive')),
  )
  office = models.ForeignKey('Office')
  charge_detail = models.CharField(max_length=3, choices=CHARGE_DETAILS)
  class Meta(Charge.Meta):
    db_table = u'om_administration_charge'


  
class Group(models.Model):
  '''
  the class maps the groups of counselors
  '''
  name = models.CharField(max_length=100)
  acronym = models.CharField(blank=True, max_length=16)
  counselors = models.ManyToManyField('InstitutionCharge', through='GroupHasCharge')
  
class GroupHasCharge(models.Model):
  '''
  maps the historical composition of council groups, this is only valid for InstitutionCharges
  
  '''
  group = models.ForeignKey('Group')
  charge = models.ForeignKey('InstitutionCharge')
  charge_description = models.CharField(blank=True, max_length=255)
  start_date = models.DateField()
  end_date = models.DateField()

  class Meta:
    db_table = u'om_group_has_charge'


class Body(models.Model):
  '''
  base class for the body, uses the Abstract Class inheritance model
  '''
  name = models.CharField(max_length=255)

  class Meta:
    abstract = True
    verbose_name_plural = u'Bodies'
  
class Institution(Body):
  '''
  institutional bodies can be of different types and the types are mapped in institution_type
  it has a relation with itself, in order to map hierarchical bodies (joint committee, ...)
  '''
  INSTITUTION_TYPES = Choices(
    ('may', _('Mayor')),    
    ('cou', _('Standard')),
    ('cig', _('City government')),
    ('com', _('Committee')),
    ('jco', _('Joint committee')),
  )
  parent = models.ForeignKey('Institution', related_name='sub_bodies_set')
  institution_type = models.CharField(max_length=3, choices=INSTITUTION_TYPES)

class Company(Body):
  '''
  company owned by the municipality, whose executives are nominated politically
  '''
  class Meta(Body.Meta):
    verbose_name_plural = u'Companies'
  
class Office(Body):
  '''
  internal municipality office, that plays a role in the administration of the municipalities
  '''
  pass


class Sitting(models.Model):
  idnum = models.CharField(blank=True, max_length=64)
  sitting_date = models.DateField()
  institution = models.ForeignKey('Institution')
  
  
class Minute(TimeStampedModel):
  title = models.CharField(max_length=255)
  sitting = models.ForeignKey('Sitting')
  minute_date = models.DateField(null=True, blank=True)
  text = models.TextField(blank=True)
  text_url = models.CharField(max_length=255, blank=True)
  pdf_file = models.FileField(upload_to="minutes/%Y%d%m", blank=True)
  pdf_url = models.CharField(max_length=255, blank=True)

  def __unicode__(self):
    return u'%s' % self.title

class Outcome(models.Model):
  sitting = models.ForeignKey('Sitting')
  act = models.OneToOneField('Act')  

class Decision(models.Model):
  ofice = models.ForeignKey('Office')
  act = models.OneToOneField('Act')  
    