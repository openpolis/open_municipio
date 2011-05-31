from django.db import models
from django.utils.translation import ugettext as _
from model_utils import Choices
from model_utils.models import TimeStampedModel, StatusModel, TimeFramedModel
from model_utils.managers import InheritanceManager


class Act(TimeStampedModel):
  '''
  This is the base class for all the different act types: it contains the common fields for
  deliberations, interrogations, interpellations, motions, agendas and emendations
  
  It is a TimeStampedModel, so it tracks creation and modification timestamps for each record.
  
  Inheritance is done through multi-table inheritance, since browsing the whole set of acts may be useful.
  The default Manager is the model_utils.managers.InheritanceManager (https://bitbucket.org/carljm/django-model-utils/src),
  that enables the select_subclasses() method, allowing the retrieval of subclasses, when needed.
  '''
  idnum = models.CharField(max_length=128, blank=True, help_text="A string representing the identification number or sequence, used internally by the administration.")
  title = models.CharField(max_length=196, blank=True)
  adj_title = models.CharField(max_length=196, blank=True, help_text="An adjoint title, added to further explain an otherwise cryptic title")
  presentation_date = models.DateField(null=True, help_text="Date of publication, as stated in the act")
  text = models.TextField(blank=True)
  process_steps = models.ManyToManyField('Process', through='ProcessStep')
  presenters = models.ManyToManyField('InstitutionCharge', db_table='om_act_presenter', related_name='act_presentations')
  recipients = models.ManyToManyField('InstitutionCharge', db_table='om_act_recipient', related_name='act_destinations')

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
  answer_type = models.CharField(max_length=3, choices=ANSWER_TYPES)
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
  charge_type = models.ForeignKey('ChargeType')
  start_date = models.DateField()
  end_date = models.DateField()
  end_reason = models.CharField(blank=True, max_length=255)

  class Meta:
    abstract = True

class InstitutionCharge(Charge):
  '''
  this is a charge in the institution (city council, city government, mayor)
  '''
  substitutes = models.OneToOneField('InstitutionCharge', blank=True, null=True, related_name='reverse_substitutes')
  substituted_by = models.OneToOneField('InstitutionCharge', blank=True, null=True, related_name='reverse_substituted_by')
  class Meta(Charge.Meta):
    db_table = u'om_institution_charge'

class OrganizationCharge(Charge):
  '''
  this is a charge in a company or organization controlled by the municipality (partecipate)
  '''  
  class Meta(Charge.Meta):
    db_table = u'om_organization_charge'

class AdministrationCharge(Charge):
  '''
  this is a charge in the internal municipality administration
  '''
  class Meta(Charge.Meta):
    db_table = u'om_administration_charge'


  
class ChargeType(models.Model):
  '''
  this maps the different charges, within each macro-category
  i.e. mayor, council president, councelor, city government member, ... for institution charges
  president, administrator, director, for organization charges
  director, officer, for administration charges
  '''
  name = models.CharField(max_length=255)
  is_elected = models.BooleanField(default=False)
  class Meta:
    db_table = u'om_charge_type'


class Group(models.Model):
  '''
  the class maps the groups of counselors
  '''
  name = models.CharField(max_length=100)
  acronym = models.CharField(blank=True, max_length=16)
  counselors = models.ManyToManyField('InstitutionCharge', through='GroupHasCharge')
  
class GroupHasCharge(models.Model):
  group = models.ForeignKey('Group')
  charge = models.ForeignKey('InstitutionCharge')
  charge_type = models.CharField(blank=True, max_length=255)
  start_date = models.DateField()
  end_date = models.DateField()

  class Meta:
    db_table = u'om_group_has_charge'
  