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

class VotationsInline(admin.TabularInline):
    model = Votation
    fields = ('n_legal', 'n_presents', 'n_maj', 'n_yes', 'n_no', 'n_abst', 'outcome')
    
admin.site.register(Votation, VotationAdminWithGroupsAndChargesVotes)
admin.site.register(GroupVote)
admin.site.register(ChargeVote)
