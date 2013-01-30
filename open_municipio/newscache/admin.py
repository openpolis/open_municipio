from django.contrib import admin
from open_municipio.newscache.models import *

class NewsAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    list_filter = ('priority', 'news_type')

admin.site.register(News, NewsAdmin)


