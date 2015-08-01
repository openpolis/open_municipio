from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext as _
from django.db.models import Q

import datetime

class FilterActiveCharge(SimpleListFilter):

    title = _("active charges")

    parameter_name = "is_active"

    def lookups(self, request, model_admin):
        
        return(
            ('1', _('yes')),
            ('0', _('no')),
        )

    def queryset(self, request, queryset):

        value = self.value()

        print "filter value: %s" % value

        if value:
            is_active = (value == '1')
            today = datetime.date.today()

            if is_active:
                queryset = queryset.exclude(end_date__lt=today).exclude(start_date__gt=today)
            else:
                queryset = queryset.filter(Q(end_date__lt=today) | Q(start_date__gt=today))

        return queryset

