__author__ = 'guglielmo'

from django.contrib import admin
from open_municipio.data_import.models import *

class FileImportAdmin(admin.ModelAdmin):
    list_filter = ('import_type', 'import_started_at')
    search_fields = ('file_path',)


admin.site.register(FileImport, FileImportAdmin)

