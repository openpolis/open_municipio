from httplib import HTTP
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from open_municipio.votations.models import ChargeVote, GroupVote, Votation  
from open_municipio.votations.filters import VotationIsLinkedToAct, VotationByYearFilterSpec, VotationByMonthFilterSpec

from .filters import VoteHasActiveCharge, ChargeVoteByYearFilterSpec, ChargeVoteByMonthFilterSpec


class GroupVoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'votation', 'group', 'vote')
    list_filter = ('group', 'votation__id')


class ChargeVoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'votation', 'charge', 'charge_group_at_vote_date', 'vote', 'sitting_date', )
    readonly_fields = [ 'charge_group_at_vote_date', 'sitting_date', ]
    list_filter = ('vote', 'is_rebel', VoteHasActiveCharge, ChargeVoteByYearFilterSpec, ChargeVoteByMonthFilterSpec )
    raw_id_fields = ['votation', 'charge']
    search_fields = ['charge__person__first_name', 'charge__person__last_name', ]

    def charge_group_at_vote_date(self, object):
        return object.charge_group_at_vote_date
    charge_group_at_vote_date.short_description = _('Charge group at vote date')

    def sitting_date(self, object):
        return object.votation.sitting.date
    sitting_date.short_description = _("sitting date")

class GroupVoteInline(admin.TabularInline):
    model = GroupVote
    extra = 1

    def get_readonly_fields(self, request, obj=None):
        ro_fields = self.model._meta.get_all_field_names()
        return ro_fields
    
        
class ChargeVoteInline(admin.TabularInline):
    model = ChargeVote
    raw_id_fields = ('charge', )
    extra = 1


class VotationAdmin(admin.ModelAdmin):
    search_fields = ('act_descr','idnum', )
    list_display = ('idnum', 'act_descr', 'sitting', 'is_linked_col','outcome')
    list_filter = ('outcome', VotationIsLinkedToAct, VotationByYearFilterSpec, VotationByMonthFilterSpec, )
    raw_id_fields = ['act','sitting',]
    readonly_fields = ('sitting', 'idnum' )
    ordering = ['-sitting__date']

    # add inlines only for superuser users
    def change_view(self, request, object_id, extra_context=None):

        if request.user.is_superuser:
            self.inlines = [GroupVoteInline, ChargeVoteInline]
        else:
            self.inlines = []
            # self.fields = ('idnum', 'sitting', 'act', 'act_descr')

        self.inline_instances = []
        for inline_class in self.inlines:
            inline_instance = inline_class(self.model, self.admin_site)
            self.inline_instances.append(inline_instance)

        return super(VotationAdmin, self).change_view(request, object_id)

    def is_linked_col(self, object):
        return object.is_linked
    is_linked_col.boolean = True
    is_linked_col.short_description = _('is linked')


class VotationsInline(admin.TabularInline):
    model = Votation
    fields = ('n_legal', 'n_presents', 'n_maj', 'n_yes', 'n_no', 'n_abst', 'outcome')

admin.site.register(Votation, VotationAdmin)
admin.site.register(GroupVote, GroupVoteAdmin)
admin.site.register(ChargeVote, ChargeVoteAdmin)
