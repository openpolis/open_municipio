from django.contrib import admin 
from django.utils.translation import ugettext_lazy as _
from open_municipio.people.models import *
from open_municipio.votations.admin import VotationsInline

class PersonAdmin(admin.ModelAdmin):
    search_fields = ['^first_name', '^last_name']
    prepopulated_fields = {"slug": ("first_name","last_name","birth_date", "birth_location",)}
  
class ChargeAdmin(admin.ModelAdmin):
    raw_id_fields = ('person', )

class GroupChargeInline(admin.TabularInline):
    model = GroupCharge
    raw_id_fields = ('charge', )
    extra = 1
  
class GroupIsMajorityInline(admin.TabularInline):
    model = GroupIsMajority
    extra = 1

class GroupAdminWithCharges(admin.ModelAdmin):
    list_display = ('name', 'acronym', 'is_majority_now')
    inlines = [GroupIsMajorityInline, GroupChargeInline]
    

class ChargeInline(admin.StackedInline):
    raw_id_fields = ('person', )
    fieldsets = (
        (None, {
            'fields': (('person', 'charge_type', 'start_date', 'end_date'), )
        }),
        (_('Advanced options'), {
            'classes': ('collapse',),
            'fields': ('description', 'end_reason')
        })
    )
    extra = 1
  
class CompanyChargeInline(ChargeInline):
    model = CompanyCharge

class AdministrationChargeInline(ChargeInline):
    model = AdministrationCharge

class InstitutionChargeInline(ChargeInline):
    model = InstitutionCharge
    raw_id_fields = ('person', 'substitutes', 'substituted_by')
    fieldsets = (
        (None, {
            'fields': (('person', 'charge_type', 'op_charge_id', 'start_date', 'end_date'), )
        }),
        (_('Advanced options'), {
            'classes': ('collapse',),
            'fields': ('description', 'end_reason', ('substitutes', 'substituted_by'))
        })
    )



class ChargeAdmin(admin.ModelAdmin):
    pass
  
class CompanyChargeAdmin(ChargeAdmin):
    model = CompanyCharge
    raw_id_fields = ('person', 'company')
    fieldsets = (
        (None, {
            'fields': (('person', 'charge_type', 'company'), 
                ('start_date', 'end_date', 'end_reason'), 
                 'description')
        }),
    )

class AdministrationChargeAdmin(ChargeAdmin):
    model = AdministrationCharge
    raw_id_fields = ('person', 'office')
    fieldsets = (
        (None, {
            'fields': (('person', 'charge_type', 'office'), 
                 ('start_date', 'end_date', 'end_reason'), 
                 'description')
        }),
    )

class InstitutionChargeAdmin(ChargeAdmin):
    model = InstitutionCharge
    raw_id_fields = ('person', 'substitutes', 'substituted_by', 'institution')
    fieldsets = (
        (None, {
            'fields': (('person', 'charge_type', 'op_charge_id', 'institution'), 
                 ('start_date', 'end_date', 'end_reason'), 
                 'description',
                 ('substitutes', 'substituted_by'))
        }),
    )


class BodyAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

class CompanyAdmin(BodyAdmin):
    inlines = [CompanyChargeInline]
class OfficeAdmin(BodyAdmin):
    inlines = [AdministrationChargeInline]
class InstitutionAdmin(BodyAdmin):
    inlines = [InstitutionChargeInline]
  
  

class SittingAdmin(admin.ModelAdmin):
    inlines = [VotationsInline]
    
admin.site.register(Sitting, SittingAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Group, GroupAdminWithCharges)
admin.site.register(InstitutionCharge, InstitutionChargeAdmin)
admin.site.register(CompanyCharge, CompanyChargeAdmin)
admin.site.register(AdministrationCharge, AdministrationChargeAdmin)
admin.site.register(Institution, InstitutionAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Office, OfficeAdmin)
