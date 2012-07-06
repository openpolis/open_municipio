from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import permalink
from django.utils.datetime_safe import date
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from model_utils import Choices
from model_utils.managers import PassThroughManager

from sorl.thumbnail import ImageField

from open_municipio.monitoring.models import Monitoring, MonitorizedItem
from open_municipio.newscache.models import NewsTargetMixin
from open_municipio.people.managers import TimeFramedQuerySet
from open_municipio.om_utils.models import SlugModel



#
# People, charges and groups
#

class Person(SlugModel, MonitorizedItem):
    # FIXME: are those constants really necessary? (given that we use ``Choices``)
    FEMALE_SEX = 0
    MALE_SEX = 1
    # FIXME: maybe ``GENDERS`` would be more appropriate, here.
    SEX = Choices(
        (MALE_SEX, _('Male')),    
        (FEMALE_SEX, _('Female')),
        )
    first_name = models.CharField(_('first name'), max_length=128)
    last_name = models.CharField(_('last name'), max_length=128)
    birth_date = models.DateField(_('birth date'))
    birth_location = models.CharField(_('birth location'), blank=True, max_length=128)
    sex = models.IntegerField(_('sex'), choices=SEX)
    op_politician_id = models.IntegerField(_('openpolis politician ID'), blank=True, null=True)
    # FIXME: find a more descriptive name
    img = ImageField(upload_to="person_images", blank=True, null=True)
    
    class Meta:
        verbose_name = _('person')
        verbose_name_plural = _('people')
   
    def __unicode__(self):
        return '%s %s' % (self.first_name, self.last_name)
    
    @permalink
    def get_absolute_url(self):
        return 'om_politician_detail', (), { 'slug': self.slug }

    def calculate_slug(self):
        slug = slugify("%s %s %s" % (self.first_name, self.last_name, self.birth_date))
        return slug

    @property
    def is_om_user(self):
        """
        Check whether this person is a registered user of OpenMunicipio.
        """
        try:
            self.userprofile
        except ObjectDoesNotExist:
            return False
        else:
            return True

    @property
    def full_name(self):
        return "%s %s" % (self.first_name, self.last_name)
   
    @property
    def all_institution_charges(self):
        """
        Return the queryset of all institution charges 
        held by this person during his/her career.
        """
        return self.institutioncharge_set.select_related().all()
    
    @property
    def current_institution_charges(self):
        """
        Return the queryset of institution charges currently 
        being held by this person (except committee-related charges).
        """
        return self.institutioncharge_set.select_related().current().exclude(
            institution__institution_type__in=(Institution.COMMITTEE, Institution.JOINT_COMMITTEE)
        )

    @property
    def current_committee_charges(self):
        return self.institutioncharge_set.select_related().current().filter(
            institution__institution_type__in=(Institution.COMMITTEE, Institution.JOINT_COMMITTEE)
        ).order_by('-institutionresponsability__charge_type')

    def current_institution_charge(self, institution):
        return self.institutioncharge_set.select_related().current().get(
            institution=institution
        )

    def has_current_charges(self):
        if self.institutioncharge_set.current().count() > 0:
            return True
        else:
            return False
    has_current_charges.short_description = _('Current')

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

    @property
    def age(self):
        """
        Returns an integer of year between birth_date and now
        """
        #end_date = in_date if in_date else date.today()
        return (date.today() - self.birth_date).days / 365


class Resource(models.Model):
    """
    This class maps the internet resources (mail, web sites, rss, facebook, twitter, )
    It must be subclassed, by a PersonResource, InstitutionResource or GroupResource class.

    The `value` field contains the resource.
    The `description` field may be used to specify the context.

    A `PERSON` resource may be a secretary, a responsible. We're interested only in
    her name, it must not be mapped into the system.
    """
    RES_TYPE = Choices(
        ('EMAIL', 'email', _('email')),
        ('URL', 'url', _('url')),
        ('PHONE', 'phone', _('phone')),
        ('FAX', 'fax', _('fax')),
        ('SNAIL', 'snail', _('snail mail')),
        ('PERSON', 'person', _('person')),
    )
    resource_type = models.CharField(verbose_name=_('type'), max_length=10, choices=RES_TYPE)
    value = models.CharField(verbose_name=_('value'), max_length=64)
    description = models.CharField(verbose_name=_('description'), max_length=255, blank=True)

    class Meta:
        abstract = True
        verbose_name = _('Resource')


class PersonResource(Resource):
    person = models.ForeignKey('Person', verbose_name=_('person'), related_name='resource_set')


class InstitutionResource(Resource):
    institution = models.ForeignKey('Institution', verbose_name=_('institution'), related_name='resource_set')


class GroupResource(Resource):
    group = models.ForeignKey('Group', verbose_name=_('group'), related_name='resource_set')


class Charge(NewsTargetMixin):
    """
    This is the base class for the different macro-types of charges (institution, organization, administration).

    The ``related_news`` attribute can be used to fetch news items related to a given charge.
    """
    person = models.ForeignKey('Person', verbose_name=_('person'))
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'), blank=True, null=True)
    end_reason = models.CharField(_('end reason'), blank=True, max_length=255)
    description = models.CharField(_('description'), blank=True, max_length=255,
                                   help_text=_('Insert the complete description of the charge, if it gives more information than the charge type'))
    
    objects = PassThroughManager.for_queryset_class(TimeFramedQuerySet)()

    class Meta:
        abstract = True

    def get_absolute_url(self):
        return self.person.get_absolute_url()


class ChargeResponsability(models.Model):
    """
    Describe a responsability that a charge has inside that charge's *container*. 
    It integrates the composition relation.

    For example: a counselor may be the City Council's president.

    This is an abstract class, that must be subclassed in order to specify
    the context (institution charge or group charge).
    """
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'), blank=True, null=True)
    description = models.CharField(_('description'), blank=True, max_length=255,
                                   help_text=_('Insert an extended description of the responsability'))

    objects = PassThroughManager.for_queryset_class(TimeFramedQuerySet)()

    class Meta:
        abstract = True


class InstitutionCharge(Charge):
    """
    This is a charge within an institutional body (City Council, City Government, Mayor, Committee).
    """
    # FIXME: one of ``substitutes`` and ``substituted_by`` field is a redundant, so it should be removed.
    # In fact, the data structure they implement is a (double) linked list, which need only one pointer
    # to the next/previous list item to navigate the list. The other one may be implemented as a cache field.
    substitutes = models.OneToOneField('self', blank=True, null=True,
                     related_name='reverse_substitute_set',
                     on_delete=models.PROTECT,
                     verbose_name=_('in substitution of'))
    substituted_by = models.OneToOneField('self', blank=True, null=True,
                     related_name='reverse_substituted_by_set',
                     on_delete=models.PROTECT,
                     verbose_name=_('substituted by'))
    institution = models.ForeignKey('Institution', on_delete=models.PROTECT, verbose_name=_('institution'), related_name='charge_set')
    op_charge_id = models.IntegerField(_('Openpolis institution charge ID'), blank=True, null=True)
    # ???
    original_charge = models.ForeignKey('self', blank=True, null=True,
                                           related_name='committee_charge_set',
                                           verbose_name=_('original institution charge'))
    ## cache fields
    n_rebel_votations = models.IntegerField(default=0)
    n_present_votations = models.IntegerField(default=0)
    n_absent_votations = models.IntegerField(default=0)

    class Meta(Charge.Meta):
        db_table = u'people_institution_charge'
        verbose_name = _('institution charge')
        verbose_name_plural = _('institution charges')

    def __unicode__(self):
        if self.denomination:
            return "%s %s - %s" % (self.person.first_name, self.person.last_name, self.denomination)
        else:
            return "%s %s" % (self.person.first_name, self.person.last_name)

    # TODO: model validation: check that ``substitutes`` and ``substituted_by`` fields
    # point to ``InstitutionCharge``s of the same kind

    @property
    def denomination(self):
        # FIXME: some kind of dis-entanglement needed here !
        # FIXME: this seems to be presentational logic, 
        # so it should be placed within the template layer
        institution_type = self.institution.institution_type
        if institution_type == Institution.INSTITUTION_TYPES.mayor:
            # QUESTION: why ``translate`` is used here ?
            return _('Mayor').translate(settings.LANGUAGE_CODE)
        elif institution_type == Institution.INSTITUTION_TYPES.city_government:
            if self.responsabilities.count():
                # QUESTION: what happens if this charge has more than one responsability?
                s = self.responsabilities[0].get_charge_type_display()
                if self.responsabilities[0].charge_type == InstitutionResponsability.CHARGE_TYPES.first_deputy_mayor:
                    s += ", %s" % self.description
                return "%s: %s - %s" % (s, self.responsabilities[0].start_date, self.responsabilities[0].end_date)
            else:
                return " %s" % self.description
        elif institution_type == Institution.INSTITUTION_TYPES.council:
            if self.responsabilities.count():
                # QUESTION: what happens if this charge has more than one responsability?
                return "%s Consiglio Comunale: %s - %s" % \
                       (self.responsabilities[0].get_charge_type_display(),
                        self.responsabilities[0].start_date, self.responsabilities[0].end_date)
                return "%s Consiglio Comunale" % self.responsabilities[0].get_charge_type_display()
            else:
                return _('Counselor').translate(settings.LANGUAGE_CODE)
        elif institution_type == Institution.INSTITUTION_TYPES.committee:
            if self.responsabilities.count():
                # QUESTION: what happens if this charge has more than one responsability?
                return "%s: %s - %s" % (self.responsabilities[0].get_charge_type_display(),
                                        self.responsabilities[0].start_date,
                                        self.responsabilities[0].end_date)
            else:
                # QUESTION: why ``translate`` is used here ?
                return _('Member').translate(settings.LANGUAGE_CODE)
        else:
            return ''

    @property
    def committee_charges(self):
        return self.committee_charge_set.all()

    @property
    def responsabilities(self):
        return self.institutionresponsability_set.all()


    @property
    def presented_acts(self):
        """
        A queryset of acts presented by this charge.
        """
        return self.presented_act_set.all()

    @property
    def received_acts(self):
        """
        A queryset of acts received by this charge.
        """
        return self.received_act_set.all()

    @property
    def charge_type(self):
        """
        Return the basic charge type translated string, according to the institution.

        For example: the council president's basic type is counselor.
        """
        # FIXME: this seems to be presentational logic, 
        # so it should be placed within the template layer
        institution_type = self.institution.institution_type
        if institution_type == Institution.INSTITUTION_TYPES.mayor:
            return _('Mayor')
        elif institution_type == Institution.INSTITUTION_TYPES.city_government:
            return _('City government member')
        elif institution_type == Institution.INSTITUTION_TYPES.council:
            return _('Counselor')
        elif institution_type == Institution.INSTITUTION_TYPES.committee:
            return _('Committee member')
        else:
            return _('Unknown charge type!')

    @property
    def council_group(self):
        """
        Return the City Council's group this charge currently belongs to (if any).

        DEPRECATED: use `self.council_current_groupcharge.group`
        """
        # FIXME: consider removing this method, 
        # according to the deprecation statement in the docstring
        return self.current_groupcharge.group

    @property
    def current_groupcharge(self):
        """
        Return the current group related to a council charge (``end_date`` is NULL).
        A single GroupCharge object is returned. The group may be accessed by the `.group` attribute

        A Council Institution charge MUST have one group.
        Other types of charge do not have a group, so None is returned.
        """
        # TODO: refine docstring
        # TODO: review implementation
        if self.institution.institution_type == Institution.COUNCIL:
            return GroupCharge.objects.select_related().get(charge__id=self.id, end_date__isnull=True)
        elif self.institution.institution_type == Institution.COMMITTEE or \
             self.institution.institution_type == Institution.JOINT_COMMITTEE:
            return GroupCharge.objects.select_related().get(charge__id=self.original_charge_id, end_date__isnull=True)
        else:
            return None

    @property
    def historical_groupcharges(self):
        """
        Return the list of past groups related to a council charge (end_date is not null).
        A list of GroupCharge objects is returned. The group may be accessed by the `.group` attribute
        """
        # TODO: refine docstring
        # TODO: review implementation
        if self.institution.institution_type == Institution.COUNCIL:
            return GroupCharge.objects.select_related().filter(charge__id=self.id, end_date__isnull=False)
        else:
            return []

    def compute_rebellion_cache(self):
        """
        Re-compute the number of votations where the charge has vote differently from her group
        and update the n_rebel_votations counter
        """
        # TODO: rename to ``_update_rebellion_cache``
        # TODO: refine docstring
        # TODO: review implementation
        self.n_rebel_votations = self.chargevote_set.filter(is_rebel=True).count()
        self.save()

    def compute_presence_cache(self):
        """
        Re-compute the number of votations where the charge was present/absent
        and update the respective counters
        """
        # TODO: rename to ``_update_attendance_cache``
        # TODO: refine docstring
        # TODO: review implementation
        from open_municipio.votations.models import ChargeVote
         
        absent = ChargeVote.VOTES.absent
        self.n_present_votations = self.chargevote_set.exclude(vote=absent).count()
        self.n_absent_votations = self.chargevote_set.filter(vote=absent).count()
        self.save()


class InstitutionResponsability(ChargeResponsability):
    """
    Responsability for institutional charges.
    """
    # FIXME: maybe this should be named ``RESPONSABILITY_TYPES`` ?
    CHARGE_TYPES = Choices(
        ('MAYOR', 'mayor', _('Mayor')),
        ('FIRST_DEPUTY_MAYOR', 'first_deputy_mayor', _('First deputy mayor')),
        ('PRESIDENT', 'president', _('President')),
        ('VICE', 'vice', _('Vice president')),
        ('VICE_VICE', 'vice_vice', _('Vice vice president')),
                                      )
    # the institutionale charge this responsability refers to
    charge = models.ForeignKey(InstitutionCharge, verbose_name=_('charge'))
    # responsability type
    charge_type = models.CharField(_('charge type'), max_length=16, choices=CHARGE_TYPES)

    class Meta:
        verbose_name = _('institutional responsability')
        verbose_name_plural = _('institutional responsabilities')


class CompanyCharge(Charge):
    """
    This is a charge within a municipality-controlled company  (IT: "Azienda Partecipata").
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
    charge_set = models.ManyToManyField('InstitutionCharge', through='GroupCharge')

    img = ImageField(upload_to="group_images", blank=True, null=True)

    class Meta:
        verbose_name = _('group')
        verbose_name_plural = _('groups')

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.acronym)

    @property
    def leader(self):
        """
        The current leader of the Group as GroupResponsability.
        None if not found.

        To fetch the InstitutionCharge, .groupcharge.charge.
        """
        try:
            leader = GroupResponsability.objects.select_related().get(
                charge__group=self,
                charge_type=GroupResponsability.CHARGE_TYPES.leader,
                end_date__isnull=True
            )
            return leader
        except ObjectDoesNotExist:
            return None

    @property
    def deputy(self):
        """
        The current deputy leader of the Group as GroupResponsability.
        None if not found.

        To fetch the InstitutionCharge, .groupcharge.charge.
        """
        try:
            deputy = GroupResponsability.objects.select_related().get(
                charge__group=self,
                charge_type=GroupResponsability.CHARGE_TYPES.deputy,
                end_date__isnull=True
            )
            return deputy
        except ObjectDoesNotExist:
            return None

    @property
    def members(self):
        """
        Current members of the group, as institution charges, leader and
        council president and vice presidents **excluded**.
        """
        return self.institution_charges.select_related().exclude(
            groupcharge__groupresponsability__charge_type__in=(
                GroupResponsability.CHARGE_TYPES.leader,
                GroupResponsability.CHARGE_TYPES.deputy
                ),
            groupcharge__groupresponsability__end_date__isnull=True
        ).exclude(
            groupcharge__charge__institutionresponsability__charge_type__in=(
                InstitutionResponsability.CHARGE_TYPES.president,
                InstitutionResponsability.CHARGE_TYPES.vice
            )
        )

    @property
    def alpha_members(self):
        """
        Alphabetically sorted members
        """
        return self.members.order_by('person__last_name')

    @property
    def institution_charges(self):
        """
        All current institution charges in the group, leader **included**
        """
        return self.charge_set.filter(groupcharge__end_date__isnull=True)

    @property
    def is_current(self):
        """
        returns True if the group has at least one current charge
        """
        return self.groupcharge_set.current().count() > 0

    @property
    def majority_records(self):
        return self.groupismajority_set.all()

    @property
    def is_majority_now(self):
        # only one majority record with no ``end_date`` should exists
        # at a time (i.e. the current one)
        return self.majority_records.get(end_date__isnull=True).is_majority

    @property
    def resources(self):
        return self.resource_set.all()

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

    @property
    def responsabilities(self):
        return self.groupresponsability_set.all()

    @property
    def responsability(self):
        if self.responsabilities.count() == 1:
            r = self.responsabilities[0]
            s = "%s: %s - %s" % (r.get_charge_type_display(), r.start_date, r.end_date)
            return s
        else:
            return ""

    class Meta:
        db_table = u'people_group_charge'
        verbose_name = _('group charge')
        verbose_name_plural = _('group charges')

    def __unicode__(self):
        if self.responsability:
            return "%s - %s - %s" % (self.group.acronym, self.charge.person.last_name, self.responsability)
        else:
            return "%s - %s" % (self.group.acronym, self.charge.person.last_name)


class GroupResponsability(ChargeResponsability):
    """
    Responsability for group charges.
    """
    # FIXME: maybe this should be named ``RESPONSABILITY_TYPES`` ?
    CHARGE_TYPES = Choices(
        ('LEADER', 'leader', _('Group leader')),
        ('DEPUTY', 'deputy', _('Group deputy leader')),
    )
    # the institutionale charge this responsability refers to
    charge = models.ForeignKey(GroupCharge, verbose_name=_('charge'))
    # responsability type
    charge_type = models.CharField(_('charge type'), max_length=16, choices=CHARGE_TYPES)



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
    An abstract base class modeling municipality-related bodies. 
    """
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)

    class Meta:
        abstract = True
    
    def __unicode__(self):
        return u'%s' % (self.name,)
    
    # FIXME: this logic pertains to the template layer
    # e.g., it may be implemented as a ``lower`` template filter
    @property
    def lowername(self):
        return self.name.lower()
  
  
class Institution(Body):
    """
    An institutional body.
    
    Different kinds of institutional bodies exist: 
    see the ``INSTITUTION_TYPES`` attribute for a full list.
    
    This model declares a `recursive relationship`_ , in order to be able to represent 
    hierarchical bodies (for example: joint committees).

    .. _`recursive relationship`: https://docs.djangoproject.com/en/1.3/ref/models/fields/#recursive-relationships
    """
    INSTITUTION_TYPES = Choices(
      (1, 'mayor', _('Mayor')),    
      (2, 'city_government', _('City Government')),
      (3, 'council', _('City Council')),
      (4, 'committee', _('Committee')),
      (5, 'joint_committee', _('Joint Committee')),
    )
    # the parent body (if any)
    parent = models.ForeignKey('self', related_name='child_body_set', blank=True, null=True)
    # the type of this institution
    institution_type = models.IntegerField(choices=INSTITUTION_TYPES)
    
    class Meta(Body.Meta):
        verbose_name = _('institution')
        verbose_name_plural = _('institutions')
          
    def get_absolute_url(self):
        if self.institution_type == Institution.INSTITUTION_TYPES.mayor:
            return reverse("om_institution_mayor")
        elif self.institution_type == Institution.INSTITUTION_TYPES.city_government:
            return reverse("om_institution_citygov")
        elif self.institution_type == Institution.INSTITUTION_TYPES.council:
            return reverse("om_institution_council")
        elif self.institution_type == Institution.INSTITUTION_TYPES.committee:
            return reverse("om_institution_committee", kwargs={'slug': self.slug})
    
    @property
    def charges(self):
        """
        A queryset of all *current* charges (``InstitutionCharge`` instances) 
        associated with this institution.
        """
        return self.charge_set.current()

    @property
    def first_deputy(self):
        """
        The current first deputy mayor of this m as InstitutionResponsability.
        None if not found.

        To access the charge: firstdeputy.charge
        """
        try:
            return InstitutionResponsability.objects.select_related().get(
                charge__institution=self,
                charge_type=InstitutionResponsability.CHARGE_TYPES.firstdeputymayor,
                end_date__isnull=True
            )
        except ObjectDoesNotExist:
            return None

    @property
    def president(self):
        """
        The current president of the institution as InstitutionResponsability.
        None if not found.

        To access the charge: pres.charge
        """
        try:
            pres = InstitutionResponsability.objects.select_related().get(
                charge__institution=self,
                charge_type=InstitutionResponsability.CHARGE_TYPES.president,
                end_date__isnull=True
            )
            return pres
        except ObjectDoesNotExist:
            return None


    @property
    def vicepresidents(self):
        """
        The current vice presidents of the institution, as InstitutionResponsabilities

        There can be more than one vicepresident.

        To access the charge: vp.charge
        """
        return InstitutionResponsability.objects.select_related().filter(
            charge__institution=self,
            charge_type=InstitutionResponsability.CHARGE_TYPES.vice,
            end_date__isnull=True
        )

    @property
    def members(self):
        """
        Members of the institution, as charges.
        Current mayor, first deputy, president and vice presidents **excluded**.
        """
        return self.charges.exclude(
            institutionresponsability__charge_type__in=(
                InstitutionResponsability.CHARGE_TYPES.mayor,
                InstitutionResponsability.CHARGE_TYPES.firstdeputymayor,
                InstitutionResponsability.CHARGE_TYPES.president,
                InstitutionResponsability.CHARGE_TYPES.vice,
                ),
            institutionresponsability__end_date__isnull=True
        ).select_related()


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

    @property
    def resources(self):
        return self.resource_set.all()

    

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
        return u'seduta num. %s del %s (%s)' % (self.number, self.date.strftime('%d/%m/%Y'), self.institution.name)
     

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
        return Institution.objects.select_related().get(institution_type=Institution.MAYOR)
    
    @property
    def as_charge(self):
        """
        A municipality mayor, as a *charge*.
        """
        return InstitutionCharge.objects.select_related().get(institution__institution_type=Institution.MAYOR)
    
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
    def charges(self):
        """
        All current members of the municipality council (aka *counselors*), as charges.
        President and vice-presidents **included**.
        """
        return self.as_institution.charges.select_related()

    @property
    def president(self):
        """
        The current president of the city council as InstitutionResponsability
        None if not found.
        """
        return  self.as_institution.president


    @property
    def vicepresidents(self):
        """
        The current vice presidents of the city council, as InstitutionResponsabilities

        There can be more than one vicepresident
        """
        return self.as_institution.vicepresidents.select_related()

    @property
    def members(self):
        """
        Members of the municipality council (aka *counselors*), as charges.
        Current president and vice presidents **excluded**.
        """
        return self.as_institution.members.select_related()

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
        return Group.objects.select_related().all()
    
    @property
    def majority_groups(self):
        """
        Counselors' groups belonging to majority.
        """
        qs = Group.objects.select_related().filter(groupismajority__end_date__isnull=True).filter(groupismajority__is_majority=True)
        return qs
    
    @property
    def minority_groups(self):
        """
        Counselors' groups belonging to minority.
        """
        qs = Group.objects.select_related().filter(groupismajority__end_date__isnull=True).filter(groupismajority__is_majority=False)
        return qs

    @property
    def acts(self):
        """
        The QuerySet of all acts emitted by the City Council.
        
        Note that the objects comprising the resulting QuerySet aren't generic ``Act`` instances,
        but instances of specific ``Act`` subclasses (i.e. ``Deliberation``, ``Motion``, etc.).
        """
        return self.as_institution.select_related().emitted_acts
    
    @property
    def deliberations(self):
        """
        The QuerySet of all deliberations emitted by the City Council.
        """
        from open_municipio.acts.models import Deliberation
        return Deliberation.objects.select_related().filter(emitting_institution=self.as_institution)
    
    @property
    def interrogations(self):
        """
        The QuerySet of all interrogations emitted by the City Council.
        """
        from open_municipio.acts.models import Interrogation
        return Interrogation.objects.select_related().filter(emitting_institution=self.as_institution)
    
    @property
    def interpellations(self):
        """
        The QuerySet of all interpellations emitted by the City Council.
        """
        from open_municipio.acts.models import Interpellation
        return Interpellation.objects.select_related().filter(emitting_institution=self.as_institution)
            
    @property
    def motions(self):
        """
        The QuerySet of all motions emitted by the City Council.
        """
        from open_municipio.acts.models import Motion
        return Motion.objects.select_related().filter(emitting_institution=self.as_institution)
    
    @property
    def agendas(self):
        """
        The QuerySet of all agendas emitted by the City Council.
        """
        from open_municipio.acts.models import Agenda
        return Agenda.objects.select_related().filter(emitting_institution=self.as_institution)


class CityGovernment(object):
    @property
    def as_institution(self):
        """
        A municipality government, as an *institution*.
        """
        return Institution.objects.get(institution_type=Institution.CITY_GOVERNMENT)
    
    @property
    def charges(self):
        """
        Members of a municipality government (mayor and first deputy included), as charges.
        """
        return self.as_institution.charges.select_related()

    @property
    def firstdeputy(self):
        """
        Returns the first deputy mayor, if existing, None if not existing
        """
        return  self.as_institution.firstdeputy

    @property
    def members(self):
        """
        Members of a municipality government (mayor and first deputy excluded), as charges.
        """
        return self.as_institution.members.select_related()

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
        return Deliberation.objects.select_related().filter(emitting_institution=self.as_institution)
    
    @property
    def interrogations(self):
        """
        The QuerySet of all interrogations emitted by the City Government.
        """
        from open_municipio.acts.models import Interrogation
        return Interrogation.objects.select_related().filter(emitting_institution=self.as_institution)
    
    @property
    def interpellations(self):
        """
        The QuerySet of all interpellations emitted by the City Government.
        """
        from open_municipio.acts.models import Interpellation
        return Interpellation.objects.select_related().filter(emitting_institution=self.as_institution)
            
    @property
    def motions(self):
        """
        The QuerySet of all motions emitted by the City Government.
        """
        from open_municipio.acts.models import Motion
        return Motion.objects.select_related().filter(emitting_institution=self.as_institution)
    
    @property
    def agendas(self):
        """
        The QuerySet of all agendas emitted by the City Government.
        """
        from open_municipio.acts.models import Agenda
        return Agenda.objects.select_related().filter(emitting_institution=self.as_institution)


class Committees(object):
    def as_institution(self):
        """
        Municipality committees, as *institutions*.
        """
        # FIXME: Should we include joint committees here?
        # (Institution.JOINT_COMMITTEE)
        return Institution.objects.select_related().filter(
            institution_type__in=(Institution.COMMITTEE, Institution.JOINT_COMMITTEE)
        )



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
