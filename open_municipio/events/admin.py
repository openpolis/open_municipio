from django.contrib import admin

from open_municipio.events.models import *


class EventAdmin(admin.ModelAdmin):
    pass

admin.site.register(Event, EventAdmin)

