from django.contrib import admin
from open_municipio.monitoring.models import *


class MonitoringAdmin(admin.ModelAdmin):
    list_display = [ 'user', 'content_type', 'object_pk', 'content_object', 'created_at' ]


admin.site.register(Monitoring, MonitoringAdmin)
