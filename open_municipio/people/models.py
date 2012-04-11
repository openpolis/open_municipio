from django.db import models
from django.db.models import permalink
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from model_utils import Choices
from model_utils.managers import PassThroughManager

from open_municipio.monitoring.models import Monitoring, MonitorizedItem
from open_municipio.newscache.models import News
from open_municipio.people.managers import TimeFramedQuerySet
from open_municipio.om_utils.models import SlugModel

import datetime



#
# Persons, charges and groups
#

class Person(models.Model, MonitorizedItem):
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

    # manager to handle the list of monitoring having as content_object this instance
    monitoring_set = generic.GenericRelation(Monitoring, object_id_field='object_pk')
    
    class Meta:
        verbose_name = _('person')
        verbose_name_plural = _('people')
   
    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)

    def save(self, *args, **kwargs):
        if self.slug is None:
            self.slug = slugify("%s %s %s" % (self.first_name, self.last_name, self.birth_date))
        super(Person, self).save(*args, **kwargs)

    @permalink
    def get_absolute_url(self):
        return 'om_politician_detail', (), { 'slug': self.slug }
    
    @property
    def full_name(self):
        return "%s %s" % (self.first_name, self.last_name)
   
    @property
    def all_institution_charges(self):
        """
        Returns the QuerySet of all institution charges held by this person during his/her career.
        """
        return self.institutioncharge_set.all()
    
    @property
    def current_institution_charges(self):
        """
        Returns a QuerySet of institution charges currently held by this person.
        """
        return self.institutioncharge_set.current()

    @property
    def resources(self):
        """
        Returns the list of resources associated with this person
        """
        return self.resource_set.all()
    
    @property
    def content_type_id(self):
        """
        Return id of the content type associated with this instance.
        """
        return ContentType.objects.get_for_model(self).id

class Resource(models.Model):
    """
    This class maps the internet resources (mail, web sites, rss, facebook, twitter, )
    """
    RES_TYPE = Choices(
        ('EMAIL', 'email', _('email')),
        ('URL', 'url', _('url')),
        ('PHONE', 'phone', _('phone')),
        ('SNAIL', 'snail', _('snail mail')),
    )
    person = models.ForeignKey('Person', verbose_name=_('person'))
    resource_type = models.CharField(verbose_name=_('type'), max_length=5, choices=RES_TYPE)
    value = models.CharField(verbose_name=_('value'), max_length=64)
    description = models.CharField(verbose_name=_('description'), max_length=255, blank=True)


class Charge(models.Model):
    """
    This is the base class for the different macro-types of charges (institution, organization, administration).

    The ``related_news`` attribute can be used  to fetch
    news related to it (or its subclasses) from ``newscache.News``

    The class inherits from ``NewsTargetMixin``, that allows the ``related_news`` attribute, to fetch
    news related to it (or its subclasses) from ``newscache.News``

    """
    person = models.ForeignKey('Person', verbose_name=_('person'))
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'), blank=True, null=True)
    end_reason = models.CharField(_('end reason'), blank=True, max_length=255)
    description = models.CharField(_('description'), blank=True, max_length=255,
                                   help_text=_('Insert the complete description of the charge, if it gives more information than the charge type'))
    
    objects = PassThroughManager.for_queryset_class(TimeFramedQuerySet)()

    # manager to handle the list of news that have the act as related object
    related_news = generic.GenericRelation(News,
                                           content_type_field='related_content_type',
                                           object_id_field='related_object_pk')

    class Meta:
        abstract = True

    def get_absolute_url(self):
        return self.person.get_absolute_url()

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
    institution = models.ForeignKey('Institution', on_delete=models.PROTECT, verbose_name=_('institution'), related_name='charge_set')
    charge_type = models.IntegerField(_('charge type'), choices=CHARGE_TYPES)
    op_charge_id = models.IntegerField(_('openpolis institution charge ID'), blank=True, null=True)
    n_rebel_votations = models.IntegerField(default=0)
    n_present_votations = models.IntegerField(default=0)
    n_absent_votations = models.IntegerField(default=0)

    class Meta(Charge.Meta):
        db_table = u'people_institution_charge'
        verbose_name = _('institution charge')
        verbose_name_plural = _('institution charges')


    def __unicode__(self):
        # TODO: implement ``get_charge_type_display()`` method
        return u'%s - %s dal %s' % (self.person, self.get_charge_type_display(), self.start_date.strftime('%d/%m/%Y'))

    # TODO: model validation: check that ``substitutes`` and ``substituted_by`` fields
    # point to ``InstitutionCharge``s of the same kind

    @property
    def presented_acts(self):
        """
        The QuerySet of acts presented by this charge.
        """
        return self.presented_act_set.all()

    @property
    def received_acts(self):
        """
        The QuerySet of acts received by this charge.
        """
        return self.received_act_set.all()

    @property
    def council_group(self):
        """
        Returns the city council's group this charge currently belongs to (if any).

        If the charge doesn't belong to any council's group  -- e.g. because (s)he
        is not a counselor, return ``None``.
        """
        # this property only make sense for counselors
        if self.charge_type == InstitutionCharge.COUNSELOR_CHARGE:
            # This query should return only one record, since a counselor
            # may belong to only one council group at a time.
            # If multiple records match the query, instead, a ``MultipleObjectsReturned``
            # exception will be raised, providing a useful integrity check for data
            group = Group.objects.get(groupcharge__charge__id=self.id, groupcharge__end_date__isnull=True)
            return group
        else:
            return None

    def compute_rebellion_cache(self):
        """
        Re-compute the number of votations where the charge has vote differently from her group
        and update the n_rebel_votations counter
        """
        self.n_rebel_votations = self.chargevote_set.filter(is_rebel=True).count()
        self.save()

    def compute_presence_cache(self):
        """
        Re-compute the number of votations where the charge was present/absent
        and update the respective counters
        """
        from open_municipio.votations.models import ChargeVote
         
        absent = ChargeVote.ABSENT
        self.n_present_votations = self.chargevote_set.exclude(vote=absent).count()
        self.n_absent_votations = self.chargevote_set.filter(vote=absent).count()
        self.save()


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
    
    company = models.ForeignKey('Company', on_delete=models.PROTECT, verbose_name=_('company'), related_name='charge_set')
    charge_type = models.IntegerField(_('charge type'), choices=CHARGE_TYPES)
    
    class Meta(Charge.Meta):
        db_table = u'people_organization_charge'
        verbose_name = _('organization charge')
        verbose_name_plural = _('organization charges')
    
    def __unicode__(self):
        # TODO: implement ``get_charge_type_display()`` method
        return u'%s - %s' % (self.get_charge_type_display(), self.company.name)
    
    
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
    
    office = models.ForeignKey('Office', on_delete=models.PROTECT, verbose_name=_('office'), related_name='charge_set')
    charge_type = models.IntegerField(_('charge type'), choices=CHARGE_TYPES)

    class Meta(Charge.Meta):
        db_table = u'people_administration_charge'
        verbose_name = _('administration charge')
        verbose_name_plural = _('administration charges')
    
    def __unicode__(self):
        # TODO: implement ``get_charge_type_display()`` method
        return u'%s - %s' % (self.get_charge_type_display(), self.office.name)
  
  
class Group(models.Model):
    """
    This model represents a group of counselors.
    """
    name = models.CharField(max_length=100)
    acronym = models.CharField(blank=True, max_length=16)
    counselor_set = models.ManyToManyField('InstitutionCharge', through='GroupCharge')

    class Meta:
        verbose_name = _('group')
        verbose_name_plural = _('groups')

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.acronym)

    @property
    def counselors(self):
        """
        Return a QuerySet containing the counselors (as charges) currently
        belonging to this group.
        """
        now = datetime.datetime.now()
        # filter out non-current ``GroupCharges`` records
        current_Q = Q(groupcharge__start_date__lte=now) & (Q(groupcharge__end_date__gte=now) | Q(groupcharge__end_date__isnull=True))
        qs = InstitutionCharge.objects.current().filter(current_Q).filter(groupcharge__group__id=self.id)
        return qs

    @property
    def majority_records(self):
        return self.groupismajority_set.all()

    @property
    def is_majority_now(self):
        # only one majority record with no ``end_date`` should exists
        # at a time (i.e. the current one)
        return self.majority_records.get(end_date__isnull=True).is_majority


class GroupCharge(models.Model):
    """
    This model records the historical composition of council groups. 
    
    This only makes sense for ``InstitutionCharges``.
    """
    group = models.ForeignKey('Group')
    charge = models.ForeignKey('InstitutionCharge')
    charge_description = models.CharField(blank=True, max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    end_reason = models.CharField(blank=True, max_length=255)
    
    objects = PassThroughManager.for_queryset_class(TimeFramedQuerySet)()    
    
    class Meta:
        db_table = u'people_group_charge'
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
    
    objects = PassThroughManager.for_queryset_class(TimeFramedQuerySet)() 

    class Meta:
        verbose_name = _('group majority')
        verbose_name_plural = _('group majorities')
    
    def __unicode__(self):
        if self.is_majority:
            return u'yes'
        elif self.is_majority is False:
            return u'no'
        else:
            return u'na'
            


#
# Bodies
#
class Body(SlugModel):
    """
    The base model for bodies. 
    
    Uses the *abstract base class* inheritance model.
    """
    name = models.CharField(_('name'), max_length=255)
    slug = models.SlugField(unique=True, blank=True, null=True, help_text=_('Suggested value automatically generated from name, must be unique'))
    description = models.TextField(_('description'), blank=True)
  
    class Meta:
        abstract = True
    
    def __unicode__(self):
        return u'%s' % (self.name,)
    
  
  
class Institution(Body):
    """
    Institutional bodies can be of different types (as specified by the ``institution_type`` field).
    
    This model has a relation with itself, in order to map hierarchical bodies (joint committees, ...).
    """
    MAYOR = 1
    CITY_GOVERNMENT = 2
    COUNCIL = 3
    COMMITTEE = 4
    JOINT_COMMITTEE = 5
    INSTITUTION_TYPES = Choices(
      (MAYOR, _('Mayor')),    
      (COUNCIL, _('Council')),
      (CITY_GOVERNMENT, _('Town government')),
      (COMMITTEE, _('Committee')),
      (JOINT_COMMITTEE, _('Joint committee')),
    )
    
    parent = models.ForeignKey('Institution', related_name='sub_body_set', blank=True, null=True)
    institution_type = models.IntegerField(choices=INSTITUTION_TYPES)
    
    class Meta(Body.Meta):
        verbose_name = _('institution')
        verbose_name_plural = _('institutions')
    
    def save(self, *args, **kwargs):
        """slugify name on first save"""
        if not self.id:
            self.slug = slugify(self.name)
        super(Institution, self).save(*args, **kwargs)
        
    def get_absolute_url(self):
        if self.institution_type == self.MAYOR:
            return reverse("om_institution_mayor")
        elif self.institution_type == self.CITY_GOVERNMENT:
            return reverse("om_institution_citygov")
        elif self.institution_type == self.COUNCIL:
            return reverse("om_institution_council")
        elif self.institution_type == self.COMMITTEE:
            return reverse("om_institution_committee", kwargs={'slug': self.slug})
    
    @property
    def charges(self):
        """
        The QuerySet of all *current* charges (``InstitutionCharge`` instances) 
        associated with this institution.  
        """
        return self.charge_set.current()
    
    @property
    def emitted_acts(self):
        """
        The QuerySet of all acts emitted by this institution.
        
        Note that the objects comprising the resulting QuerySet aren't generic ``Act`` instances,
        but instances of specific ``Act`` subclasses (i.e. ``Deliberation``, ``Motion``, etc.).
        This is made possible by the fact that the default manager for the ``Act`` model is 
        ``model_utils.managers.InheritanceManager``, and this manager class declares 
        ``use_for_related_fields = True``.   See `Django docs`_ for details.
        
        .. _`Django docs`: https://docs.djangoproject.com/en/1.3/topics/db/managers/#controlling-automatic-manager-types
        """
        # NOTE: See also Django bug #14891
        return self.emitted_act_set.all().select_subclasses()
    
    

class Company(Body):
    """
    A company owned by the municipality, whose executives are nominated politically.
    """
    class Meta(Body.Meta):
        verbose_name = _('company')
        verbose_name_plural = _('companies')

    def get_absolute_url(self):
        return reverse("om_company_detail", kwargs={'slug': self.slug})
    
    @property
    def charges(self):
        """
        The QuerySet of all *current* charges (``CompanyCharge`` instances) 
        associated with this company.  
        """
        return self.charge_set.current()
 
    
  
class Office(Body):
    """
    Internal municipality office, playing a role in municipality's administration.
    """
    class Meta(Body.Meta):
        verbose_name = _('office')
        verbose_name_plural = _('offices')

    def get_abolute_url(self):
        return reverse("om_office_detail", kwargs={'slug': self.slug})
    
    @property
    def charges(self):
        """
        The QuerySet of all *current* charges (``AdministrationCharge`` instances) 
        associated with this office.  
        """
        return self.charge_set.current()
    
#
# Sittings
#
class Sitting(models.Model):
    """
    WRITEME
    """
    idnum = models.CharField(blank=True, max_length=64)
    date = models.DateField()
    number = models.IntegerField(blank=True, null=True)
    institution = models.ForeignKey(Institution, on_delete=models.PROTECT)
 
    class Meta:
        verbose_name = _('sitting')
        verbose_name_plural = _('sittings')
    
    def __unicode__(self):
        return u'seduta num. %s del %s' % (self.number, self.date.strftime('%d/%m/%Y'))
     

## Private DB access API

class Mayor(object):
    """
    A municipality mayor (both as a charge and an institution).
    """
     
    @property
    def as_institution(self):
        """
        A municipality mayor, as an *institution*.
        """
        return Institution.objects.get(institution_type=Institution.MAYOR)
    
    @property
    def as_charge(self):
        """
        A municipality mayor, as a *charge*.
        """
        return self.as_institution.charges[0]
    
    @property
    def acts(self):
        """
        The QuerySet of all acts emitted by the mayor (as an institution).
        
        Note that the objects comprising the resulting QuerySet aren't generic ``Act`` instances,
        but instances of specific ``Act`` subclasses (i.e. ``Deliberation``, ``Motion``, etc.).
        """
        return self.as_institution.emitted_acts
    

class CityCouncil(object):
    @property
    def as_institution(self):
        """
        A municipality council, as an *institution*.
        """
        return Institution.objects.get(institution_type=Institution.COUNCIL)
    
    @property
    def members(self):
        """
        Members of a municipality council (aka *counselors*), as charges.
        """
        return self.as_institution.charges
    
    @property
    def majority_members(self):
        """
        Majority counselors, as charges.
        """
        # FIXME: this method should return a QuerySet, non a Set
        result = set()
        for majority_group in self.majority_groups:
            result.add(majority_group.counselors)            
        return result
    
    @property
    def minority_members(self):
        """
        Minority counselors, as charges.
        """
        # FIXME: this method should return a QuerySet, non a Set
        result = set()
        for minority_group in self.minority_groups:
            result.add(minority_group.counselors)            
        return result
        
    @property
    def groups(self):
        """
        Groups of counselors within of a municipality council.
        """
        return Group.objects.all()
    
    @property
    def majority_groups(self):
        """
        Counselors' groups belonging to majority.
        """
        qs = Group.objects.filter(groupismajority__end_date__isnull=True).filter(groupismajority__is_majority=True)
        return qs
    
    @property
    def minority_groups(self):
        """
        Counselors' groups belonging to minority.
        """
        qs = Group.objects.filter(groupismajority__end_date__isnull=True).filter(groupismajority__is_majority=False)
        return qs
    
    @property
    def acts(self):
        """
        The QuerySet of all acts emitted by the City Council.
        
        Note that the objects comprising the resulting QuerySet aren't generic ``Act`` instances,
        but instances of specific ``Act`` subclasses (i.e. ``Deliberation``, ``Motion``, etc.).
        """
        return self.as_institution.emitted_acts
    
    @property
    def deliberations(self):
        """
        The QuerySet of all deliberations emitted by the City Council.
        """
        from open_municipio.acts.models import Deliberation
        return Deliberation.objects.filter(emitting_institution=self.as_institution)
    
    @property
    def interrogations(self):
        """
        The QuerySet of all interrogations emitted by the City Council.
        """
        from open_municipio.acts.models import Interrogation
        return Interrogation.objects.filter(emitting_institution=self.as_institution)
    
    @property
    def interpellations(self):
        """
        The QuerySet of all interpellations emitted by the City Council.
        """
        from open_municipio.acts.models import Interpellation
        return Interpellation.objects.filter(emitting_institution=self.as_institution)
            
    @property
    def motions(self):
        """
        The QuerySet of all motions emitted by the City Council.
        """
        from open_municipio.acts.models import Motion
        return Motion.objects.filter(emitting_institution=self.as_institution)
    
    @property
    def agendas(self):
        """
        The QuerySet of all agendas emitted by the City Council.
        """
        from open_municipio.acts.models import Agenda
        return Agenda.objects.filter(emitting_institution=self.as_institution)


class CityGovernment(object):
    @property
    def as_institution(self):
        """
        A municipality government, as an *institution*.
        """
        return Institution.objects.get(institution_type=Institution.CITY_GOVERNMENT)
    
    @property
    def members(self):
        """
        Members of a municipality government (aka *assessors*), as charges.
        """
        return self.as_institution.charges

    @property
    def acts(self):
        """
        The QuerySet of all acts emitted by the city government (as an institution).
        
        Note that the objects comprising the resulting QuerySet aren't generic ``Act`` instances,
        but instances of specific ``Act`` subclasses (i.e. ``Deliberation``, ``Motion``, etc.).
        """
        return self.as_institution.emitted_acts
    
    @property
    def deliberations(self):
        """
        The QuerySet of all deliberations emitted by the City Government.
        """
        from open_municipio.acts.models import Deliberation
        return Deliberation.objects.filter(emitting_institution=self.as_institution)
    
    @property
    def interrogations(self):
        """
        The QuerySet of all interrogations emitted by the City Government.
        """
        from open_municipio.acts.models import Interrogation
        return Interrogation.objects.filter(emitting_institution=self.as_institution)
    
    @property
    def interpellations(self):
        """
        The QuerySet of all interpellations emitted by the City Government.
        """
        from open_municipio.acts.models import Interpellation
        return Interpellation.objects.filter(emitting_institution=self.as_institution)
            
    @property
    def motions(self):
        """
        The QuerySet of all motions emitted by the City Government.
        """
        from open_municipio.acts.models import Motion
        return Motion.objects.filter(emitting_institution=self.as_institution)
    
    @property
    def agendas(self):
        """
        The QuerySet of all agendas emitted by the City Government.
        """
        from open_municipio.acts.models import Agenda
        return Agenda.objects.filter(emitting_institution=self.as_institution)


class Committees(object):
    @property
    def as_institution(self):
        """
        Municipality committees, as *institutions*.
        """
        # FIXME: Should we include joint committees here?
        # (Institution.JOINT_COMMITTEE)
        return Institution.objects.filter(institution_type=Institution.COMMITTEE)


class Municipality(object):
    """
    A hierarchy of objects representing a municipality.
    
    Provides convenient access to insitutions, charges, groups and the like.
    """  
    def __init__(self):
        self.mayor = Mayor()
        self.gov = CityGovernment()
        self.council = CityCouncil()
        self.committees = Committees()
  
  
municipality = Municipality()
