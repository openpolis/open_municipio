from django.contrib import admin 
from django.utils.translation import ugettext_lazy as _
from django.utils.datetime_safe import date
from django.db.models import Q
from open_municipio.people.models import *
from open_municipio.votations.admin import VotationsInline
from open_municipio.acts.models import Speech
from open_municipio.widgets import SortWidget

from sorl.thumbnail.admin import AdminImageMixin

from django.contrib.admin.util import unquote
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.functional import update_wrapper
from django.utils.html import strip_spaces_between_tags as short
from django.forms import ModelForm

from open_municipio.people.forms import SittingItemFormSet, SpeechInlineForm
from open_municipio.om.admin import LinkedTabularInline

class PersonResourceInline(admin.TabularInline):
    model = PersonResource
    extra = 0


class PersonAdminWithResources(AdminImageMixin, admin.ModelAdmin):
    list_display = ('id', '__unicode__', 'has_current_charges', 'birth_date', 'birth_location' )
    list_display_links = ('__unicode__',)
    search_fields = ['^first_name', '^last_name']
    prepopulated_fields = {"slug": ("first_name","last_name","birth_date", "birth_location",)}
    inlines = [PersonResourceInline, ]


class ChargeAdmin(admin.ModelAdmin):
    raw_id_fields = ('person', )


class GroupResourceInline(admin.TabularInline):
    model = GroupResource
    extra = 0


class GroupChargeInline(admin.TabularInline):
    model = GroupCharge
    raw_id_fields = ('charge', )
    extra = 1
  

class GroupIsMajorityInline(admin.TabularInline):
    model = GroupIsMajority
    extra = 0


class InCouncilNow(admin.SimpleListFilter):

    title = _("In council now")

    parameter_name = "in_council_now"

    def lookups(self, request, model_admin):
    
        return(
            ('1', _('Yes')),   
            ('0', _('No')),
        )
    
    def queryset(self, request, queryset):
    
        val = self.value()

        today = date.today()

        # note: groups with no related item (groupismajority) will be considered
        # as not in council

        if val == '1':
            queryset = queryset.exclude(groupismajority__isnull=True).filter(Q(groupismajority__end_date__gt=today) | Q(groupismajority__end_date__isnull=True))

        elif val == '0':
            # the check for groups NOT in majority is more complex because
            # we have to check that ALL related objects (groupismajority)
            # have an end_date previous the current date
            groups_in_council = Group.objects.exclude(groupismajority__isnull=True).filter(Q(groupismajority__end_date__gt=today) | Q(groupismajority__end_date__isnull=True))

            queryset = queryset.exclude(pk__in=groups_in_council)

        return queryset   


class GroupAdminWithCharges(AdminImageMixin, admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('name', 'acronym', 'is_majority_now', 'in_council_now')
    inlines = [GroupResourceInline, GroupIsMajorityInline, GroupChargeInline]

    list_filter = [ InCouncilNow, 'groupismajority__is_majority' ]
 
    ordering = [ 'name', 'acronym' ]   

    def is_majority_now(self, obj):
        return obj.is_majority_now
    is_majority_now.short_description = _("Is majority now")

    def in_council_now(self, obj):
        return obj.in_council_now
    in_council_now.short_description = _("In council now")

class ChargeInline(admin.StackedInline):
    raw_id_fields = ('person', )
    fieldsets = (
        (None, {
            'fields': (('person', 'start_date', 'end_date'), )
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


class InstitutionResourceInline(admin.TabularInline):
    model = InstitutionResource
    extra = 0


class InstitutionChargeInline(ChargeInline):
    model = InstitutionCharge
    raw_id_fields = ('person', 'substitutes', 'substituted_by')
    fieldsets = (
        (None, {
            'fields': (('person', 'op_charge_id', 'start_date', 'end_date'), )
        }),
        (_('Advanced options'), {
            'classes': ('collapse',),
            'fields': ('description', 'end_reason', ('substitutes', 'substituted_by'))
        })
    )


class ResponsabilityInline(admin.TabularInline):
    raw_id_fields = ('charge',)
    extra = 0


class InstitutionResponsabilityInline(ResponsabilityInline):
    model = InstitutionResponsability
    fields = ('charge', 'charge_type', 'start_date', 'end_date', 'description')


class GroupResponsabilityInline(admin.TabularInline):
    model = GroupResponsability
    raw_id_fields = ('charge',)
    extra = 0
    fields = ('charge', 'charge_type', 'start_date', 'end_date', 'description')


class ChargeAdmin(admin.ModelAdmin):
    pass


class CompanyChargeAdmin(ChargeAdmin):
    model = CompanyCharge
    raw_id_fields = ('person', 'company')
    fieldsets = (
        (None, {
            'fields': (('person', 'company'),
                ('start_date', 'end_date', 'end_reason'), 
                 'description')
        }),
    )


class AdministrationChargeAdmin(ChargeAdmin):
    model = AdministrationCharge
    raw_id_fields = ('person', 'office')
    fieldsets = (
        (None, {
            'fields': (('person', 'office'),
                 ('start_date', 'end_date', 'end_reason'), 
                 'description')
        }),
    )


class InstitutionChargeAdmin(ChargeAdmin):
    model = InstitutionCharge
    raw_id_fields = ('person', 'substitutes', 'substituted_by', 'original_charge')
    search_fields = ['^person__first_name', '^person__last_name']

    fieldsets = (
        (None, {
            'fields': (('person', 'op_charge_id', 'institution', 'original_charge'),
                 ('start_date', 'end_date', 'end_reason'), 
                  'description',
                 ('substitutes', 'substituted_by'))
        }),
        (_("Presences"), {
            'fields': (('n_present_votations', 'n_absent_votations'), ('n_present_attendances', 'n_absent_attendances'))
        }),
    )
    list_display = ('__unicode__', 'institution', 'start_date', 'end_date')
    list_select_related = True
    list_filter = ['institution__name']
    inlines = [InstitutionResponsabilityInline]



class GroupChargeAdmin(admin.ModelAdmin):
    raw_id_fields = ('charge', )
    list_display = ('__unicode__', 'start_date', 'end_date')
    list_select_related = True
    list_filter = ['group']
    inlines = [GroupResponsabilityInline]

    search_fields = [ 'charge__person__first_name', 'charge__person__last_name', 'group__name', 'group__acronym', ]


class BodyAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


class CompanyAdmin(BodyAdmin):
    inlines = [CompanyChargeInline]


class OfficeAdmin(BodyAdmin):
    inlines = [AdministrationChargeInline]


class InstitutionAdmin(BodyAdmin):

    list_filter = ("institution_type", )

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)
        info = self.model._meta.app_label, self.model._meta.module_name
        return patterns('',
                        url(r'^(.+)/move-(up)/$',
                            wrap(self.move_view),
                            name='%s_%s_move_up' % info),
                        url(r'^(.+)/move-(down)/$',
                            wrap(self.move_view),
                            name='%s_%s_move_down' % info),
                        ) + super(InstitutionAdmin, self).get_urls()

    def move_view(self, request, object_id, direction):
        obj = get_object_or_404(self.model, pk=unquote(object_id))
        if direction == 'up':
            obj.move_up()
        else:
            obj.move_down()
        return HttpResponseRedirect('../../')

    link_html = short("""
        <a href="../../%(app_label)s/%(module_name)s/%(object_id)s/move-up/">UP</a> |
        <a href="../../%(app_label)s/%(module_name)s/%(object_id)s/move-down/">DOWN</a> (%(position)s)
        """)

    def move_up_down_links(self, obj):
        return self.link_html % {
            'app_label': self.model._meta.app_label,
            'module_name': self.model._meta.module_name,
            'object_id': obj.id,
            'position': obj.position, 
        }
    move_up_down_links.allow_tags = True
    move_up_down_links.short_description = _(u'Move')

    inlines = [InstitutionResourceInline, InstitutionChargeInline]
    list_display = ('name', 'institution_type', 'move_up_down_links',)

class SpeechInline(LinkedTabularInline):
    model = Speech
    fields = ("author", "author_name_when_external", "title", \
              "seq_order", "admin_link", )
    raw_id_fields = ["author", ]
    extra = 0
    form = SpeechInlineForm

class SittingItemInline(LinkedTabularInline):
    model = SittingItem
    fields = ('title', 'related_act_set', 'item_type', 'seq_order','admin_link',)
    raw_id_fields = ('related_act_set',)
    extra = 0

    form = SittingItemFormSet


class SittingItemAdmin(admin.ModelAdmin):
    list_display = ( 'title','sitting', 'seq_order','item_type','num_related_acts')
    ordering = ('-sitting__date','seq_order')
    search_fields = ['^title', ]
    list_filter = ['sitting__institution','item_type',]

    raw_id_fields = ( 'sitting', 'related_act_set', )

    inlines = [SpeechInline, ]


class SittingAdmin(admin.ModelAdmin):
    inlines = [SittingItemInline, VotationsInline]


admin.site.register(SittingItem, SittingItemAdmin)
admin.site.register(Sitting, SittingAdmin)
admin.site.register(Person, PersonAdminWithResources)
admin.site.register(Group, GroupAdminWithCharges)
admin.site.register(GroupCharge, GroupChargeAdmin)
admin.site.register(InstitutionCharge, InstitutionChargeAdmin)
admin.site.register(CompanyCharge, CompanyChargeAdmin)
admin.site.register(AdministrationCharge, AdministrationChargeAdmin)
admin.site.register(Institution, InstitutionAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Office, OfficeAdmin)
