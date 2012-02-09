from django.contrib import admin 
from django.utils.translation import ugettext_lazy as _
from open_municipio.om.models import *

class AttachInline(admin.StackedInline): 
    model = Attach
    extra = 0

class EmendationInline(admin.StackedInline): 
    fk_name = 'act'
    model = Emendation
    extra = 0

class TransitionInline(admin.TabularInline):
    model = Transition
    extra = 1

class ActAdmin(admin.ModelAdmin):
    pass

class ActAdminWithAttaches(admin.ModelAdmin):
    inlines = [AttachInline, TransitionInline]

class ActAdminWithEmendations(admin.ModelAdmin):
    inlines = [EmendationInline]

class ActAdminWithAttachesAndEmendations(admin.ModelAdmin):
    inlines = [AttachInline, EmendationInline, TransitionInline]

class StatusAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

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
admin.site.register(Act, ActAdmin)
admin.site.register(Motion, ActAdminWithEmendations)
admin.site.register(Agenda, ActAdminWithEmendations)
admin.site.register(Emendation, ActAdminWithAttaches)
  
'''
admin.site.register(Attach)
admin.site.register(Status, StatusAdmin)
admin.site.register(Decision)
admin.site.register(Votation, VotationAdminWithGroupsAndChargesVotes)
admin.site.register(GroupVote)
admin.site.register(ChargeVote)
'''
