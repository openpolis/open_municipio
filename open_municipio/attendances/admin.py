from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Attendance, ChargeAttendance
from open_senigallia.votations.filters import VotationIsLinkedToAct, \
                            VotationByYearFilterSpec, VotationByMonthFilterSpec


class AttendanceAdmin(admin.ModelAdmin):
    
    search_fields = ('act_descr', 'idnum', 'act__title', 'act__adj_title',)
    list_filter = ('outcome', VotationIsLinkedToAct, VotationByYearFilterSpec,
                    VotationByMonthFilterSpec,) 
    raw_id_fields = ['act','sitting',]
    ordering = ['sitting__date',]
    list_display = ['idnum', 'act_descr', 'sitting', 'is_linked_col', 'outcome',]

    def is_linked_col(self, object):
        return object.is_linked
    is_linked_col.boolean = True
    is_linked_col.short_description = _('is linked')


class ChargeAttendanceAdmin(admin.ModelAdmin):

    raw_id_fields = ['attendance', 'charge',]

    list_display = ("charge", "attendance", "value")
    list_filter = ("value", "charge",)


admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(ChargeAttendance, ChargeAttendanceAdmin)
