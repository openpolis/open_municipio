from django.contrib import admin 
from om.models import Deliberation, Interrogation, Interpellation, Motion, Agenda, AttachedDocument, Emendation, Process, ProcessStep

class DocumentInline(admin.StackedInline): 
  model = AttachedDocument
  extra = 0

class EmendationInline(admin.StackedInline): 
  fk_name = 'act'
  model = Emendation
  extra = 0

class ProcessStepInline(admin.TabularInline):
  model = ProcessStep
  extra = 1

class ActAdminWithDocuments(admin.ModelAdmin):
  inlines = [DocumentInline, ProcessStepInline]

class ActAdminWithEmendations(admin.ModelAdmin):
  inlines = [EmendationInline]

class ActAdminWithDocumentsAndEmendations(admin.ModelAdmin):
  inlines = [DocumentInline, EmendationInline, ProcessStepInline]

class ProcessAdmin(admin.ModelAdmin):
  pass

admin.site.register(Deliberation, ActAdminWithDocumentsAndEmendations)
admin.site.register(Interrogation)
admin.site.register(Interpellation)
admin.site.register(Motion, ActAdminWithEmendations)
admin.site.register(Agenda, ActAdminWithEmendations)
admin.site.register(Emendation, ActAdminWithDocuments)
admin.site.register(AttachedDocument)
admin.site.register(Process, ProcessAdmin)