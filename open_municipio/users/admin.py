from django.contrib import admin, auth
from open_municipio.users.models import *
from open_municipio.people.models import *

class ProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ('user', 'person')

class OMUserAdmin(auth.admin.UserAdmin):
    list_display_extra = ( "is_active", )

    def changelist_view(self, request, extra_context=None):

        self.list_display += self.list_display_extra

        return super(OMUserAdmin, self).changelist_view(request, extra_context)

    class Meta:
        app_label = "auth"


admin.site.register(UserProfile, ProfileAdmin)

try:
    admin.site.unregister(auth.models.User)
except NotRegistered:
    # do nothing
    pass

admin.site.register(auth.models.User, OMUserAdmin)
