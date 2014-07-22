from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Attendance, ChargeAttendance
from open_senigallia.votations.filters import VotationIsLinkedToAct, \
                            VotationByYearFilterSpec, VotationByMonthFilterSpec

class ChargeAttendanceInline(admin.TabularInline):
    
    model = ChargeAttendance

    fields = [ "attendance", "charge", "value", ]



class AttendanceAdmin(admin.ModelAdmin):
    
    search_fields = ('act_descr', 'idnum', 'act__title', 'act__adj_title',)
    list_filter = (VotationIsLinkedToAct, VotationByYearFilterSpec,
                    VotationByMonthFilterSpec,) 
    raw_id_fields = ['act','sitting',]
    ordering = ['sitting__date',]
    list_display = ['idnum', 'act_descr', 'sitting', 'is_linked_col','n_presents', 'n_absents']

    def is_linked_col(self, object):
        return object.is_linked
    is_linked_col.boolean = True
    is_linked_col.short_description = _('is linked')

    inlines = [ ChargeAttendanceInline, ]


class ChargeAttendanceAdmin(admin.ModelAdmin):

    raw_id_fields = ['attendance', 'charge',]

    list_display = ("charge", "attendance", )
#    list_filter = ("value", )



admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(ChargeAttendance, ChargeAttendanceAdmin)
