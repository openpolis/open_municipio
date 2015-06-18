#from open_municipio.people.models import Person, InstitutionCharge, \
#    CompanyCharge, AdministrationCharge
from django.db import models
import datetime
from model_utils import Choices
from django.utils.translation import ugettext_lazy as _

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

#from open_municipio.people.models import Charge


import logging

class Provider(models.Model):
    desc = models.CharField(max_length=255, verbose_name=_('description'))

    def __unicode__(self):
        return u"%s" % self.desc
    
    class Meta:
        verbose_name=_('provider')
        verbose_name_plural=_('providers')

class LookupObject(models.Model):
    local = None
    external = None
    provider = None

    class Meta:
        abstract = True

    @staticmethod
    def extract_active(lookup_objs, as_of):
        from open_municipio.people.models import Charge
        
        found = None
        
        for curr_obj in lookup_objs:
            if isinstance(curr_obj, Charge):
                
                if not curr_obj.is_in_charge(as_of):
                    continue                
                
                if found:
                    raise ValueError("More than one active object correspond: date=%s, 1st found=%s, 2nd found=%s" % (as_of, found, curr_obj))
                
                found = curr_obj
            else:
                raise ValueError("Current object is not of supported type: (Charge, ). Passed: %s" % (curr_obj, ))
        
        return found

    @staticmethod
    def lookup(objects, external, provider, as_of=None):
        #return objects.get(external=external, provider=provider).local
        lookup_objs = objects.filter(external=external, provider=provider)
        
        local_objs = map(lambda x: x.local, lookup_objs)
        
        if len(local_objs) > 0 and as_of is not None:
            found = LookupObject.extract_active(local_objs, as_of)
        elif len(local_objs) == 1:
            found = local_objs[0]
        elif len(local_objs) > 1:
            raise ValueError("Too many occurrence of external id %s (no date passed). Found: %s" % 
                             (external, local_objs, ))
        else:
            # no object found
            #raise ValueError("No correspondence found for external id %s (as of %s)" % (external, as_of, ))
            found = None
        
        return found

    def __str__(self):
        return "%s [%s > %s]" % (self.local, self.provider, self.external)

    def __unicode__(self):
        return u"%s [%s > %s]" % (self.local, self.provider, self.external)


class LookupPerson(LookupObject):
    from open_municipio.people.models import Person
    
    local = models.ForeignKey(Person,verbose_name=_('OM id'))
    external = models.CharField(max_length=256,verbose_name=_('provider id'))
    provider = models.ForeignKey(Provider,verbose_name=_('provider'))

    @staticmethod
    def lookup(external, provider):
        return LookupObject.lookup(LookupPerson.objects, external)

    class Meta:
        verbose_name = _("lookup person")
        verbose_name = _("lookup persons")


class LookupInstitutionCharge(LookupObject):
    from open_municipio.people.models import InstitutionCharge
    
    local = models.ForeignKey(InstitutionCharge,verbose_name=_('OM id'))
    external = models.CharField(max_length=256,verbose_name=_('provider id'))
    provider = models.ForeignKey(Provider,verbose_name=_('provider'))

    @staticmethod
    def lookup(external, provider, as_of):
        return LookupObject.lookup(LookupInstitutionCharge.objects, 
            external, provider, as_of)

    @property
    def person(self):
        return self.local.person

    @property
    def institution(self):
        return self.local.institution

    class Meta:
        unique_together = (('local','external','provider'),)
        verbose_name = _("lookup institution charge")
        verbose_name_plural = _("lookup institution charges")
   

class LookupCompanyCharge(LookupObject):
    from open_municipio.people.models import CompanyCharge
    
    local = models.ForeignKey(CompanyCharge,verbose_name=_('OM id'))
    external = models.CharField(max_length=256,verbose_name=_('provider id'))
    provider = models.ForeignKey(Provider,verbose_name=_('provider'))

    @staticmethod
    def lookup(external, provider, as_of):
        return LookupObject.lookup(LookupCompanyCharge.objects, external, 
            provider, as_of)

    class Meta:
        verbose_name = _("lookup company charge")
        verbose_name_plural = _("lookup company charges")
 
 
class LookupAdministrationCharge(LookupObject):
    from open_municipio.people.models import AdministrationCharge
    
    local = models.ForeignKey(AdministrationCharge,verbose_name=_('OM id'))
    external = models.CharField(max_length=256,verbose_name=_('provider id'))
    provider = models.ForeignKey(Provider,verbose_name=_('provider'))

    @staticmethod
    def lookup(external, provider, as_of):
        return LookupObject.lookup(LookupAdministrationCharge.objects, external, 
            provider, as_of)

    class Meta:
        verbose_name = _("lookup administration charge")
        verbose_name_plural = _("lookup administration charges")


class FileImport(models.Model):
    """
    Keep track of an imported data file
    """
    IMPORT_TYPE = Choices(
        ('ACT', 'act', _('act')),
        ('VOTATION', 'votation', _('votation'))
    )

    import_type = models.CharField(choices=IMPORT_TYPE, max_length=8)
    import_started_at = models.DateTimeField(_('started at'), default=datetime.datetime.now())
    import_closed_at = models.DateTimeField(_('closed at'), blank=True, null=True)
    file_path = models.CharField(_('path to file'), max_length=255)
    n_import = models.IntegerField(_('import sequence'), default=1)

    def __unicode__(self):
        started_at_date = self.import_started_at.strftime("%d.%m.%Y") if self.import_started_at else "N/A"
        started_at_time = self.import_started_at.strftime("%H:%M:%S") if self.import_started_at else "N/A"
        closed_at_time = self.import_closed_at.strftime("%H:%M:%S") if self.import_closed_at else "N/A"

        return "%s - %s (%s) @%s from %s to %s" % \
               (self.get_import_type_display(), self.file_path, self.n_import,
                started_at_date, started_at_time, closed_at_time)

    class Meta:
        db_table = u'data_import_file'
        unique_together = (('file_path', 'n_import'),)
        verbose_name = _('file import')
        verbose_name_plural = _('files import')

