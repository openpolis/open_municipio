from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

from model_utils import Choices

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
    is_majority = models.NullBooleanField(_('Is majority'), default=False, null=True)
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
# Sittings
#
class Sitting(models.Model):
    """
    WRITEME
    """
    idnum = models.CharField(blank=True, max_length=64)
    date = models.DateField()
    institution = models.ForeignKey(Institution, on_delete=models.PROTECT)
    
    class Meta:
        verbose_name = _('sitting')
        verbose_name_plural = _('sittings')
