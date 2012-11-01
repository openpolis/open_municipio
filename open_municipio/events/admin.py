from django.contrib import admin

from open_municipio.events.models import *


class EventAdmin(admin.ModelAdmin):
    raw_id_fields = ['act']

admin.site.register(Event, EventAdmin)

