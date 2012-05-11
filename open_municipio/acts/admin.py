from django.contrib import admin
from django import forms

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

class AttachInline(admin.StackedInline): 
    model = Attach
    extra = 0

class EmendationInline(admin.StackedInline): 
    fk_name = 'act'
    model = Emendation
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
            self.inlines = [PresenterInline, AttachInline, TransitionInline, EmendationInline]
            self.readonly = ['status']
        else:
            self.inlines = [TransitionInline]
            self.readonly_fields = ['idnum', 'title', 'status', 'presentation_date', 'text', 'emitting_institution']

        self.inline_instances = []
        for inline_class in self.inlines:
            inline_instance = inline_class(self.model, self.admin_site)
            self.inline_instances.append(inline_instance)

        return super(ActAdmin, self).change_view(request, object_id, extra_context)


class ActAdminWithAttaches(admin.ModelAdmin):
    inlines = [AttachInline, TransitionInline]

class ActAdminWithEmendations(admin.ModelAdmin):
    inlines = [EmendationInline]

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


admin.site.register(Act, ActAdmin)

# The following two lines restore the default admin for the class Act
# (the function "transition_form_factory" need to be fixed at line 19 of this file!)
# admin.site.unregister(Act)
# admin.site.register(Act)
# end of our homemade fix!

admin.site.register(Deliberation, DeliberationAdmin)
admin.site.register(Interrogation)
admin.site.register(Interpellation)
admin.site.register(Motion, ActAdminWithEmendations)
admin.site.register(Calendar)
admin.site.register(Emendation, ActAdminWithAttaches)
admin.site.register(Attach)
