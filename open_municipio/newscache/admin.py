from django.contrib import admin
from open_municipio.newscache.models import *

class NewsAdmin(admin.ModelAdmin):
    pass

admin.site.register(News, NewsAdmin)


