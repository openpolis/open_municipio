from open_municipio.filters import OMByYearFilterSpec, OMByMonthFilterSpec, \
                                OMBySubTypeFilterSpec
from open_municipio.acts.models import Act, Speech


class SpeechByYearFilterSpec(OMByYearFilterSpec):
    model = Speech
    field = "sitting_item__sitting__date"

    def queryset_by_year(self, queryset, year):
        return queryset.filter(sitting_item__sitting__date__year=year)

class SpeechByMonthFilterSpec(OMByMonthFilterSpec):
    model = Speech
    field = "sitting_item__sitting__date"

    def queryset_by_month(self, queryset, month):
        return queryset.filter(sitting_item__sitting__date__month=month)

class ActByYearFilterSpec(OMByYearFilterSpec):
    model = Act
    field = "presentation_date"

    def queryset_by_year(self, queryset, year):
        return queryset.filter(presentation_date__year=year)

class ActByMonthFilterSpec(OMByMonthFilterSpec):
    model = Act
    field = "presentation_date"

    def queryset_by_month(self, queryset, month):
        return queryset.filter(presentation_date__month=month)

class ActByTypeFilterSpec(OMBySubTypeFilterSpec):
    model = Act
