from django.contrib import admin, auth
from open_municipio.users.models import *
from open_municipio.people.models import *

class ProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ('user', 'person')

    list_filter = [ 'says_is_politician', 'wants_newsletter', 'location', ]
    
    search_fields = [ "user__first_name", "user__last_name", "user__email", ]



class OMUserAdmin(auth.admin.UserAdmin):
    list_display_extra = ( "is_active", "date_joined" )

    def get_list_display(self, *args, **kwargs):
        ld_base = super(OMUserAdmin, self).get_list_display(*args, **kwargs) 

        return ld_base + self.list_display_extra


    class Meta:
        app_label = "auth"


admin.site.register(UserProfile, ProfileAdmin)

try:
    admin.site.unregister(auth.models.User)
except NotRegistered:
    # do nothing
    pass

admin.site.register(auth.models.User, OMUserAdmin)
