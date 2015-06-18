from django.utils.translation import ugettext as _
from django.contrib.admin import SimpleListFilter

from ..filters import OMByYearFilterSpec, OMByMonthFilterSpec
from .models import Attendance

class AttendanceBySittingYearFilterSpec(OMByYearFilterSpec):
    model = Attendance
    field = "sitting__date"

    def queryset_by_year(self, queryset, year):
        return queryset.filter(sitting__date__year=year)


class AttendanceByMonthFilterSpec(OMByMonthFilterSpec):
    
    def queryset_by_month(self, queryset, month):
        return queryset.filter(sitting__date__month=month)


class AttendanceIsLinkedToAct(SimpleListFilter):
    title = _('is_linked')

    parameter_name = "is_linked"

    def __init__(self, *args, **kwargs):
        return super(AttendanceIsLinkedToAct, self).__init__(*args, **kwargs)

    def lookups(self, request, model_admin):
        options = ( ( "yes","yes" ), ( "no","no" ))

        return options

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.exclude(act=None)
        elif self.value() == "no":
            return queryset.filter(act=None)
        else:
            return queryset
