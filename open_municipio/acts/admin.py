from django.contrib import admin
from django import forms
from django.utils import formats
from django.db import models
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import ugettext_lazy as _

from open_municipio.acts.models import *
from open_municipio.acts.forms import SpeechAdminForm, SpeechInActInlineFormSet, \
    InterpellationAdminForm, InterrogationAdminForm
from open_municipio.acts.filters import ActByYearFilterSpec, ActByMonthFilterSpec, SpeechByYearFilterSpec,SpeechByMonthFilterSpec
from open_municipio.taxonomy.models import TaggedAct

def transition_form_factory(act_model):
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
        final_status = forms.ChoiceField(label=_('Status'), choices=act_model.STATUS)

        class Meta:
            model = Transition


    return RuntimeTransitionForm


class PresenterInline(admin.TabularInline):
    fields = ['charge', 'support_type', 'support_date']
    model = ActSupport
    extra = 0

    raw_id_fields = ( 'charge', )

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
    raw_id_fields = ( 'votation', 'attendance', )
    model = Transition
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        """
        the form used to change the model depends on the 
        parent model. the parent model is the model of the
        being edited in the main form
        so it's a deliberation, a motion, an interrogation, ...
        (note that in the ActAdmin view, the parent model is the Act class,
        this is why we check the obj.downcast() type, first)
        """

        specific_object = obj.downcast() if obj else None

        if specific_object:
            self.form = transition_form_factory(type(specific_object))
        elif self.parent_model is not None:
            self.form = transition_form_factory(self.parent_model)

        return super(TransitionInline, self).get_formset(request, obj, **kwargs)


class ActAdmin(admin.ModelAdmin):
    list_display = ('idnum', 'title', 'presentation_date', 'emitting_institution', 'status')
    search_fields = ('idnum', 'title',)
    list_filter = ( ActByYearFilterSpec, ActByMonthFilterSpec,)

    inlines_superuser = [ PresenterInline, AttachInline, TransitionInline, 
                          AmendmentInline ]
    inlines_base = [ TransitionInline]    

    readonly_fields_superuser = ['status']
    readonly_fields_base = ['idnum', 'title', 'status', 'presentation_date', 
                            'text', 'emitting_institution']

    # tag and categories are designed to work on the frontend; including them
    # here will generate errors when rendering particular configurations of tags
    exclude = ("category_set", "tag_set",)


    # genial hack to allow users with no permissions to show
    # the list of related acts for a raw field
    # adapted from: http://www.maykinmedia.nl/blog/2010/feb/9/djang-view-permissions-for-related-objects/
    #
    # pop=1 is true when a window is open as popup for raw fields lookup
    def has_change_permission(self, request, obj=None):
        return request.GET.get('pop', None) == '1' or\
               super(ActAdmin, self).has_change_permission(request, obj)

    def has_add_permission(self, rerquest):
 
        # disable adding for ActAdmin but not for its subclasses
        return self.model != Act
   

    def get_readonly_fields(self, request, *args, **kwargs):

        readonly_fields = self.readonly_fields

        if request.user.is_superuser:
            if getattr(self, "readonly_fields_superuser"):
                readonly_fields = self.readonly_fields_superuser

        else:
            if getattr(self, "Readonly_fields_base"):
                readonly_fields = self.readonly_fields_base

        return readonly_fields

    # add some inlines  for superuser users only
    def change_view(self, request, object_id, form_url='', extra_context=None):

        object = self.model.objects.get(id=object_id)

        # type(object.downcast()) returns the specific type of act (Deliberation, 
        # Interrogation, ...) even when self.model is Act (i.e. it is invoked
        # in the ActAdmin view)
        specific_object_type = type(object.downcast())

#        print "object type: %s" % specific_object_type

        self.inlines = []

        if request.user.is_superuser:
            self.inlines = self.inlines_superuser
        else:
            self.inlines = self.inlines_base

        self.inline_instances = []
        for inline_class in self.inlines:
            inline_instance = inline_class(specific_object_type, self.admin_site)
            self.inline_instances.append(inline_instance)

        return super(ActAdmin, self).change_view(request, object_id, form_url, extra_context)


class CalendarAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {'widget': FilteredSelectMultiple("Acts", is_stacked=False) },
    }
# TODO if set filter_horizontal, "Acts" label in FilteredSelectMultiple disapper
    filter_horizontal = ( 'act_set' , )


class AmendmentAdmin(ActAdmin):
    raw_id_fields = ("act", )


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

class SpeechInActInline(admin.TabularInline):
    model = ActHasSpeech
    formset = SpeechInActInlineFormSet

    verbose_name = _("Speech in act")
    verbose_name_plural = _("Speeches in act")
    raw_id_fields = ( 'speech', )


class InterrogationAdmin(ActAdmin):
    fieldsets = (
        (None, {
            'fields': ('title', 'adj_title', 'status', 'status_is_final', 'recipient_set')
        }),
        ('Presentazione', {
            'fields': ('presentation_date', 'text', 'emitting_institution'),
            }),
        ('Risposta', {
            'fields': ( 'answer_type', 'answer_date', 'answer_text', )
            }),
        )
    form = InterrogationAdminForm

    inlines_superuser = [ PresenterInline, SpeechInActInline, AttachInline, TransitionInline ]

    list_display = ( "presentation_date", "author", "title", "status", )
    list_filter = ActAdmin.list_filter + ( "status", "answer_type" )

    # due to django internal checks, we must specify "answer_date" in the 
    # attribute readonly_fields AND return it using get_readonly_fields
    readonly_fields = [ "answer_date", "status_is_final", ]

    def answer_date(self, obj):
        return formats.date_format(obj.answer_date)
    answer_date.short_description = _("answer date")

    # due to django internal checks, we must specify "answer_date" in the 
    # attribute readonly_fields AND return it using get_readonly_fields
    def get_readonly_fields(self, request, *args, **kwargs):
        fields = list( super(InterrogationAdmin, self).get_readonly_fields(request, *args, **kwargs) )

        fields.extend(["answer_date", "status_is_final"])

        return fields





class InterpellationAdmin(ActAdmin):
    fieldsets = (
        (None, {
            'fields': ('title', 'adj_title', 'status', 'status_is_final', 'recipient_set')
        }),
        ('Presentazione', {
            'fields': ('presentation_date', 'text', 'emitting_institution'),
            }),
        ('Risposta', {
            'fields': ( 'answer_type', 'answer_date', 'answer_text', ),
        }),
        )

    form = InterpellationAdminForm
    inlines_superuser = [PresenterInline, SpeechInActInline, AttachInline, TransitionInline]

    list_display = ( "presentation_date", "author", "title", "status", )

    list_filter = ActAdmin.list_filter + ("status", )

    # due to django internal checks, we must specify "answer_date" in the 
    # attribute readonly_fields AND return it using get_readonly_fields
    readonly_fields = [ "answer_date", "status_is_final", ]


    def answer_date(self, obj):
        return formats.date_format(obj.answer_date)
    answer_date.short_description = _("answer date")

    # due to django internal checks, we must specify "answer_date" in the 
    # attribute readonly_fields AND return it using get_readonly_fields
    def get_readonly_fields(self, request, *args, **kwargs):
        fields = list( super(InterpellationAdmin, self).get_readonly_fields(request, *args, **kwargs) )

        fields.extend(["answer_date", "status_is_final"])

        return fields


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
    extra = 2

    raw_id_fields = ('act', )



class SpeechAdmin(admin.ModelAdmin):

    form = SpeechAdminForm
    search_fields = ('title', 'author__last_name','author__first_name','author_name_when_external',)
    inlines = [ActInSpeechInline,]
    raw_id_fields = ('author', 'sitting_item', 'votation', )
    list_display = ( 'author_name_admin', 'seq_order', 'sitting_admin','date_admin','sitting_item')
    ordering = ('-sitting_item__sitting__date','seq_order',)

    list_filter = ( SpeechByYearFilterSpec, SpeechByMonthFilterSpec, )

class AttachAdmin(admin.ModelAdmin):

    list_display = ('title','document_date','document_type','act_title','act_type')

    search_fields = ['title', 'act__title', 'act__adj_title',]
    list_filter = [ 'document_type', ]    

    raw_id_fields = [ 'act', ]

    def attach_title(self, obj):
        return obj.title
    attach_title.short_text_description = _("title")

    def act_title(self, obj):
        act_title = ""
        if obj.act:
            act_title = obj.act.adj_title or obj.act.title

        return act_title
    act_title.short_text_description = _("act")

    def act_type(self, obj):
        act_type = None

        if obj.act:
            act_type = obj.act.get_type_name()
        return act_type

    act_type.short_text_description = _("act type")

class AgendaAdmin(ActAdmin):
    fieldsets = (
        (None, {
            'fields': ('idnum', 'title', 'adj_title', 'status')
        }),
        ('Presentazione', {
            'classes': ('collapse',),
            'fields': ('presentation_date', 'text', 'emitting_institution'),
            }),
        ('Post-approvazione', {
            'classes': ('collapse',),
            'fields': ('is_key',)
        }),
        )


class TransitionAdmin(admin.ModelAdmin):
    
    search_fields = ("id", "act__title", "act__adj_title")
    list_display = ["id", "act_short", "transition_date", "final_status"]
    list_filter = ["final_status", ]

    raw_id_fields = ["act","votation", ]
    readonly_fields = ["symbol", "final_status", ]

    def act_short(self, obj):
#        print "obj: %s" % obj
        text = u"%s" % obj.act
        if len(text) > 50:
            text = "%s..." % text[:50]
        return text
    act_short.short_description = _("act")

admin.site.register(Act, ActAdmin)

# The following two lines restore the default admin for the class Act
# (the function "transition_form_factory" need to be fixed at line 19 of this file!)
# admin.site.unregister(Act)
# admin.site.register(Act)
# end of our homemade fix!

admin.site.register(Deliberation, DeliberationAdmin)
admin.site.register(Interrogation, InterrogationAdmin)
admin.site.register(Interpellation, InterpellationAdmin)
admin.site.register(Motion, MotionAdmin)
admin.site.register(Calendar, CalendarAdmin)
admin.site.register(Amendment, AmendmentAdmin)
admin.site.register(Attach, AttachAdmin)
admin.site.register(Transition, TransitionAdmin)
admin.site.register(Speech, SpeechAdmin)
admin.site.register(Agenda, AgendaAdmin)
