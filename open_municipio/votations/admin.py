from httplib import HTTP
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from open_municipio.votations.models import ChargeVote, GroupVote, Votation  


class GroupVoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'votation', 'group', 'vote')
    list_filter = ('group', 'votation__id')


class ChargeVoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'votation', 'charge', 'charge_group_at_vote_date', 'vote')
    list_filter = ('votation__id',)


class GroupVoteInline(admin.TabularInline):
    model = GroupVote
    extra = 1


class ChargeVoteInline(admin.TabularInline):
    model = ChargeVote
    raw_id_fields = ('charge', )
    extra = 1


class VotationAdmin(admin.ModelAdmin):
    search_fields = ('act_descr','idnum', )
    list_display = ('idnum', 'act_descr', 'sitting', 'is_linked', 'outcome')
    list_filter = ('sitting',)
    raw_id_fields = ['act']
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


class VotationsInline(admin.TabularInline):
    model = Votation
    fields = ('n_legal', 'n_presents', 'n_maj', 'n_yes', 'n_no', 'n_abst', 'outcome')

admin.site.register(Votation, VotationAdmin)
admin.site.register(GroupVote, GroupVoteAdmin)
admin.site.register(ChargeVote, ChargeVoteAdmin)
