from django.contrib import admin 
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



class GroupVoteInline(admin.TabularInline):
  model = GroupVote
  extra = 1

class ChargeVoteInline(admin.TabularInline):
  model = ChargeVote
  raw_id_fields = ('charge', )
  extra = 1
 
class VotationAdminWithGroupsAndChargesVotes(admin.ModelAdmin):
  inlines = [GroupVoteInline, ChargeVoteInline] 
  
admin.site.register(Deliberation, ActAdminWithAttachesAndEmendations)
admin.site.register(Interrogation)
admin.site.register(Interpellation)
admin.site.register(Motion, ActAdminWithEmendations)
admin.site.register(Agenda, ActAdminWithEmendations)
admin.site.register(Emendation, ActAdminWithAttaches)
admin.site.register(Attach)
admin.site.register(Process, ProcessAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(InstitutionCharge, ChargeAdmin)
admin.site.register(CompanyCharge, ChargeAdmin)
admin.site.register(AdministrationCharge, ChargeAdmin)
admin.site.register(Group, GroupAdminWithCharges)
admin.site.register(Institution)
admin.site.register(Company)
admin.site.register(Office)
admin.site.register(Decision)
admin.site.register(Votation, VotationAdminWithGroupsAndChargesVotes)
admin.site.register(GroupVote)
admin.site.register(ChargeVote)