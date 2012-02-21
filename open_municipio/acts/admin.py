from django.contrib import admin

from open_municipio.acts.models import *

class PresenterInline(admin.TabularInline):
    fields = ['charge', 'support_type', 'support_date']
    model = ActSupport
    extra = 0

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

class ActAdminWithSATE(admin.ModelAdmin):
    inlines = [PresenterInline, AttachInline, TransitionInline, EmendationInline]
    fieldsets = (
        (None, {
            'fields': ('idnum', 'title', 'adj_title',)
        }),
        ('Presentazione', {
            'classes': ('collapse',),
            'fields': ('presentation_date', 'text', 'emitting_institution', 'initiative'),        
        }),
        ('Post-approvazione', {
            'classes': ('collapse',),
            'fields': ('approval_date', 'approved_text', 'publication_date', 'execution_date')
        }),
    )
    

class StatusAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Deliberation, ActAdminWithSATE)
admin.site.register(Interrogation)
admin.site.register(Interpellation)
admin.site.register(Act, ActAdmin)
admin.site.register(Motion, ActAdminWithEmendations)
admin.site.register(Calendar)
admin.site.register(Emendation, ActAdminWithAttaches)
admin.site.register(Status, StatusAdmin)
admin.site.register(Attach)

