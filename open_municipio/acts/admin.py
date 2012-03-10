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
    # genial hack to allow users with no permissions to show
    # the list of related acts for a raw field
    # adapted from: http://www.maykinmedia.nl/blog/2010/feb/9/djang-view-permissions-for-related-objects/
    #
    # pop=1 is true when a window is open as popup for raw fields lookup
    def has_change_permission(self, request, obj=None):
        return request.GET.get('pop', None) == '1' or\
               super(ActAdmin, self).has_change_permission(request, obj)

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
    

admin.site.register(Act, ActAdmin)
admin.site.register(Deliberation, ActAdminWithSATE)
admin.site.register(Interrogation)
admin.site.register(Interpellation)
admin.site.register(Motion, ActAdminWithEmendations)
admin.site.register(Calendar)
admin.site.register(Emendation, ActAdminWithAttaches)
admin.site.register(Attach)
