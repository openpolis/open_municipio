from django.db import models
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _

from django.contrib.admin import SimpleListFilter
from open_municipio.filters import OMByYearFilterSpec, OMByMonthFilterSpec
from .models import Votation

class VotationByYearFilterSpec(OMByYearFilterSpec):
    model = Votation
    field = "sitting__date"

    def queryset_by_year(self, queryset, year):
        return queryset.filter(sitting__date__year=year)


class VotationByMonthFilterSpec(OMByMonthFilterSpec):

    def queryset_by_month(self, queryset, month):
        return queryset.filter(sitting__date__month=month)


class VotationIsLinkedToAct(SimpleListFilter):
    title = _('is_linked')

    parameter_name = "is_linked"

    def __init__(self, *args, **kwargs):
        return super(VotationIsLinkedToAct, self).__init__(*args, **kwargs)

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

