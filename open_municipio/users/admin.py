from django.contrib import admin
from open_municipio.users.models import *
from open_municipio.people.models import *

class ProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ('user', 'person')

admin.site.register(UserProfile, ProfileAdmin)
