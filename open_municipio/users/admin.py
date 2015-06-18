from django.contrib import admin, auth
from open_municipio.users.models import *
from open_municipio.people.models import *

class ProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ('user', 'person')

    list_display = [ 'user', 'user_first_name', 'user_last_name', 'user_email', 'person', 'privacy_level', 'location', 'user_date_joined' ]

    list_filter = [ 'says_is_politician', 'wants_newsletter', 'location', ]

    search_fields = [ "user__first_name", "user__last_name", "user__email", ]

    def user_first_name(self, obj):
        return obj.user.first_name

    user_first_name.short_description = 'first name'
    user_first_name.admin_order_field = 'user__first_name'

    def user_last_name(self, obj):
        return obj.user.last_name

    user_last_name.short_description = 'last name'
    user_last_name.admin_order_field = 'user__last_name'

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'email'
    user_email.admin_order_field = 'user__email'

    def user_date_joined(self, obj):
        return obj.user.date_joined

    user_date_joined.short_description = 'date joined'
    user_date_joined.admin_order_field = 'user__date_joined'

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
