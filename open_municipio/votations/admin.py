from django.contrib import admin 
from django.utils.translation import ugettext_lazy as _

from open_municipio.votations.models import ChargeVote, GroupVote, Votation  


class GroupVoteInline(admin.TabularInline):
    model = GroupVote
    extra = 1

class ChargeVoteInline(admin.TabularInline):
    model = ChargeVote
    raw_id_fields = ('charge', )
    extra = 1
 
class VotationAdminWithGroupsAndChargesVotes(admin.ModelAdmin):
    inlines = [GroupVoteInline, ChargeVoteInline] 

admin.site.register(Votation, VotationAdminWithGroupsAndChargesVotes)
admin.site.register(GroupVote)
admin.site.register(ChargeVote)
