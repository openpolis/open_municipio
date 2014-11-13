from django.contrib import admin
from open_municipio.newscache.models import *

class NewsAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    list_filter = ('priority', 'news_type', 'generating_content_type')
    
    list_display = ('created', 'priority', 'news_type', 'generating_object', 'related_object', 'text')


admin.site.register(News, NewsAdmin)


