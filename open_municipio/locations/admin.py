from django.contrib import admin 
from django.utils.translation import ugettext_lazy as _
from open_municipio.locations.models import Location


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'count')

admin.site.register(Location, LocationAdmin)
