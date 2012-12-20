from open_municipio.data_import.models import LookupPerson, \
    LookupInstitutionCharge, LookupAdministrationCharge, LookupCompanyCharge, \
    Provider

from django.contrib import admin 

admin.site.register(Provider)
admin.site.register(LookupPerson)
admin.site.register(LookupInstitutionCharge)
admin.site.register(LookupAdministrationCharge)
admin.site.register(LookupCompanyCharge)

