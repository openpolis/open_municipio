from open_municipio.people.models import Person, InstitutionCharge, \
    CompanyCharge, AdministrationCharge
from django.db import models
import datetime
from django.db import models
from model_utils import Choices
from django.utils.translation import ugettext_lazy as _

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

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
    def lookup(objects, external, provider):
        return objects.get(external=external, provider=provider).local

    def __str__(self):
        return "%s [%s > %s]" % (self.local, self.provider, self.external)
    def __unicode__(self):
        return u"%s [%s > %s]" % (self.local, self.provider, self.external)

class LookupPerson(LookupObject):
    local = models.ForeignKey(Person,verbose_name=_('OM id'))
    external = models.CharField(max_length=256,verbose_name=_('provider id'))
    provider = models.ForeignKey(Provider,verbose_name=_('provider'))

    @staticmethod
    def lookup(external, provider):
        return LookupObject.lookup(LookupPerson.objects, external)

class LookupInstitutionCharge(LookupObject):
    local = models.ForeignKey(InstitutionCharge,verbose_name=_('OM id'))
    external = models.CharField(max_length=256,verbose_name=_('provider id'))
    provider = models.ForeignKey(Provider,verbose_name=_('provider'))

    @staticmethod
    def lookup(external, provider):
        return LookupObject.lookup(LookupInstitutionCharge.objects, 
            external, provider)

    class Meta:
        unique_together = (('local','external','provider'),)
    

class LookupCompanyCharge(LookupObject):
    local = models.ForeignKey(CompanyCharge,verbose_name=_('OM id'))
    external = models.CharField(max_length=256,verbose_name=_('provider id'))
    provider = models.ForeignKey(Provider,verbose_name=_('provider'))

    @staticmethod
    def lookup(external, provider):
        return LookupObject.lookup(LookupCompanyCharge.objects, external, 
            provider)

class LookupAdministrationCharge(LookupObject):
    local = models.ForeignKey(AdministrationCharge,verbose_name=_('OM id'))
    external = models.CharField(max_length=256,verbose_name=_('provider id'))
    provider = models.ForeignKey(Provider,verbose_name=_('provider'))

    @staticmethod
    def lookup(external, provider):
        return LookupObject.lookup(LookupAdministrationCharge.objects, external, 
            provider)

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
        verbose_name = _('File import')
        verbose_name_plural = _('Files import')

