from django.contrib import admin
from django import forms
from django.db import models
from django.contrib.admin.widgets import FilteredSelectMultiple

from open_municipio.acts.models import *

def transition_form_factory(act):
    """
    allows to change the final_status field in the transition form
    see: http://www.artfulcode.net/articles/runtime-choicefield-filtering-in-djangos-admin/
    see: TransitionInline class, below, too for how to use this

    final_status is a charfield in the model,
    the form field is rendered as a ChoiceField,
    the choices are dynamically generated starting from the act instance,
    passed inside the get_formset method
    """
    class RuntimeTransitionForm(forms.ModelForm):
        final_status = forms.ChoiceField(label='Status', choices=act.downcast().STATUS)

        class Meta:
            model = Transition

    return RuntimeTransitionForm


class PresenterInline(admin.TabularInline):
    fields = ['charge', 'support_type', 'support_date']
    model = ActSupport
    extra = 0


class ActInline(admin.TabularInline):
    model = Act
    extra = 0


class AttachInline(admin.StackedInline): 
    model = Attach
    extra = 0


class AmendmentInline(admin.StackedInline):
    fk_name = 'act'
    model = Amendment
    extra = 0


class TransitionInline(admin.TabularInline):
    model = Transition
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        """
        the form used to change the model depends on the obj parameter
        obj is the act being edited in the main form
        so it's a deliberation, a motion, an interrogation, ...
        """
        if obj is not None:
            self.form = transition_form_factory(obj)
        return super(TransitionInline, self).get_formset(request, obj, **kwargs)


class ActAdmin(admin.ModelAdmin):
    list_display = ('idnum', 'title', 'presentation_date', 'emitting_institution', 'status')
    search_fields = ('idnum', 'title',)

    # genial hack to allow users with no permissions to show
    # the list of related acts for a raw field
    # adapted from: http://www.maykinmedia.nl/blog/2010/feb/9/djang-view-permissions-for-related-objects/
    #
    # pop=1 is true when a window is open as popup for raw fields lookup
    def has_change_permission(self, request, obj=None):
        return request.GET.get('pop', None) == '1' or\
               super(ActAdmin, self).has_change_permission(request, obj)

    # add some inlines  for superuser users only
    def change_view(self, request, object_id, extra_context=None):

        if request.user.is_superuser:
            self.inlines = [PresenterInline, AttachInline, TransitionInline, AmendmentInline]
            self.readonly = ['status']
        else:
            self.inlines = [TransitionInline]
            self.readonly_fields = ['idnum', 'title', 'status', 'presentation_date', 'text', 'emitting_institution']

        self.inline_instances = []
        for inline_class in self.inlines:
            inline_instance = inline_class(self.model, self.admin_site)
            self.inline_instances.append(inline_instance)

        return super(ActAdmin, self).change_view(request, object_id, extra_context)


class CalendarAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {'widget': FilteredSelectMultiple("Acts", is_stacked=False) },
    }
# TODO if set filter_horizontal, "Acts" label in FilteredSelectMultiple disapper
    filter_horizontal = ( 'act_set' , )



class ActAdminWithAttaches(admin.ModelAdmin):
    inlines = [AttachInline, TransitionInline]


class ActAdminWithAmendments(admin.ModelAdmin):
    inlines = [AmendmentInline]


class MotionAdmin(ActAdmin):
    fieldsets = (
        (None, {
            'fields': ('idnum', 'title', 'adj_title', 'status')
        }),
        ('Presentazione', {
            'classes': ('collapse',),
            'fields': ('presentation_date', 'text', 'emitting_institution'),
            }),
        )


class InterrogationAdmin(ActAdmin):
    fieldsets = (
        (None, {
            'fields': ('idnum', 'title', 'adj_title', 'status')
        }),
        ('Presentazione', {
            'classes': ('collapse',),
            'fields': ('presentation_date', 'text', 'emitting_institution', 'answer_type'),
            }),
        )


class DeliberationAdmin(ActAdmin):
    fieldsets = (
        (None, {
            'fields': ('idnum', 'title', 'adj_title', 'status')
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


class ActInSpeechInline(admin.TabularInline):
    model = ActHasSpeech
    extra = 0


class SpeechAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    inlines = [ActInSpeechInline,]
    raw_id_fields = ('charge', 'sitting_item', 'votation', )

class AttachAdmin(admin.ModelAdmin):
    list_display = ('title','document_date','document_type')


admin.site.register(Act, ActAdmin)

# The following two lines restore the default admin for the class Act
# (the function "transition_form_factory" need to be fixed at line 19 of this file!)
# admin.site.unregister(Act)
# admin.site.register(Act)
# end of our homemade fix!

admin.site.register(Deliberation, DeliberationAdmin)
admin.site.register(Interrogation, InterrogationAdmin)
admin.site.register(Interpellation)
admin.site.register(Motion, MotionAdmin)
admin.site.register(Calendar, CalendarAdmin)
admin.site.register(Amendment, ActAdminWithAttaches)
admin.site.register(Attach, AttachAdmin)
admin.site.register(Transition)
admin.site.register(Speech, SpeechAdmin)
admin.site.register(Agenda)
