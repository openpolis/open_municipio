from django.contrib import admin 
from django.utils.translation import ugettext_lazy as _
from om.models import *

class AttachInline(admin.StackedInline): 
  model = Attach
  extra = 0

class EmendationInline(admin.StackedInline): 
  fk_name = 'act'
  model = Emendation
  extra = 0

class ProcessStepInline(admin.TabularInline):
  model = ProcessStep
  extra = 1

class ActAdminWithAttaches(admin.ModelAdmin):
  inlines = [AttachInline, ProcessStepInline]

class ActAdminWithEmendations(admin.ModelAdmin):
  inlines = [EmendationInline]

class ActAdminWithAttachesAndEmendations(admin.ModelAdmin):
  inlines = [AttachInline, EmendationInline, ProcessStepInline]

class ProcessAdmin(admin.ModelAdmin):
  prepopulated_fields = {"slug": ("name",)}

class PersonAdmin(admin.ModelAdmin):
  search_fields = ['^first_name', '^last_name']
  
class ChargeAdmin(admin.ModelAdmin):
  raw_id_fields = ('person', )

class GroupChargeInline(admin.TabularInline):
  model = GroupCharge
  raw_id_fields = ('charge', )
  extra = 1

class GroupAdminWithCharges(admin.ModelAdmin):
  inlines = [GroupChargeInline]


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

class CompanyAdmin(admin.ModelAdmin):
  inlines = [CompanyChargeInline]
class OfficeAdmin(admin.ModelAdmin):
  inlines = [AdministrationChargeInline]
class InstitutionAdmin(admin.ModelAdmin):
  inlines = [InstitutionChargeInline]
  
  
  
  
class GroupVoteInline(admin.TabularInline):
  model = GroupVote
  extra = 1

class ChargeVoteInline(admin.TabularInline):
  model = ChargeVote
  raw_id_fields = ('charge', )
  extra = 1
 
class VotationAdminWithGroupsAndChargesVotes(admin.ModelAdmin):
  inlines = [GroupVoteInline, ChargeVoteInline] 
  
admin.site.register(Person, PersonAdmin)
admin.site.register(Group, GroupAdminWithCharges)
admin.site.register(InstitutionCharge, InstitutionChargeAdmin)
admin.site.register(CompanyCharge, CompanyChargeAdmin)
admin.site.register(AdministrationCharge, AdministrationChargeAdmin)
admin.site.register(Institution, InstitutionAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Office, OfficeAdmin)

'''
admin.site.register(Deliberation, ActAdminWithAttachesAndEmendations)
admin.site.register(Interrogation)
admin.site.register(Interpellation)
admin.site.register(Motion, ActAdminWithEmendations)
admin.site.register(Agenda, ActAdminWithEmendations)
admin.site.register(Emendation, ActAdminWithAttaches)
admin.site.register(Attach)
admin.site.register(Process, ProcessAdmin)
admin.site.register(Decision)
admin.site.register(Votation, VotationAdminWithGroupsAndChargesVotes)
admin.site.register(GroupVote)
admin.site.register(ChargeVote)
'''
