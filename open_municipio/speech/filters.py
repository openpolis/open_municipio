from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter

class IsPublicFilter(SimpleListFilter):
    title = _("Is public")
    parameter_name = "is_public"

    def lookups(self, request, model_admin):    
        return (
            ("Any", _("Any")),
            ("Yes", _("Yes")),
            ("No", _("No")),
        )

    def queryset(self, request, queryset):
        if self.value == "Yes":
            return queryset.filter(act_status_is_final__eq=True)
        if self.value == "No":
            return queryset.filter(act_status_is_final__eq=False)


