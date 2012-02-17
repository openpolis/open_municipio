from django.contrib import admin

from open_municipio.acts.models import (Act, Agenda, Attach, Deliberation, Interpellation, 
                                        Emendation, Interrogation, Motion, Status, Transition)

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


admin.site.register(Deliberation, ActAdminWithAttachesAndEmendations)
admin.site.register(Interrogation)
admin.site.register(Interpellation)
admin.site.register(Act, ActAdmin)
admin.site.register(Motion, ActAdminWithEmendations)
admin.site.register(Agenda, ActAdminWithEmendations)
admin.site.register(Emendation, ActAdminWithAttaches)
admin.site.register(Status, StatusAdmin)
admin.site.register(Attach)

