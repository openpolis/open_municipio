__author__ = 'guglielmo'

from django.contrib import admin
from open_municipio.data_import.models import *
from django.utils.translation import ugettext as _

from open_municipio.data_import.models import LookupPerson, \
    LookupInstitutionCharge, LookupAdministrationCharge, LookupCompanyCharge, \
    Provider
from .filters import FilterActiveCharge

from django.contrib import admin 

admin.site.register(Provider)
admin.site.register(LookupPerson)
#admin.site.register(LookupInstitutionCharge)
admin.site.register(LookupAdministrationCharge)
admin.site.register(LookupCompanyCharge)

class LookupInstitutionChargeAdmin(admin.ModelAdmin):
    list_display = ('person','institution','charge_is_active','external','provider')
    list_filter = ('provider', 'local__institution',FilterActiveCharge)
    ordering = ['local__person__last_name','local__person__first_name',]

    raw_id_fields = ( 'local', )

    search_fields = [ "local__person__first_name", "local__person__last_name", ]

    def charge_is_active(self, obj):
        return obj.local.is_in_charge()
    charge_is_active.short_description = _("is in charge")
    charge_is_active.boolean = True

admin.site.register(LookupInstitutionCharge, LookupInstitutionChargeAdmin)

class FileImportAdmin(admin.ModelAdmin):
    list_filter = ('import_type', 'import_started_at')
    search_fields = ('file_path',)


admin.site.register(FileImport, FileImportAdmin)

