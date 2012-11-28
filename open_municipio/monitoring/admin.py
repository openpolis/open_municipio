from django.contrib import admin
from open_municipio.monitoring.models import *


class MonitoringAdmin(admin.ModelAdmin):
    pass


admin.site.register(Monitoring, MonitoringAdmin)
