from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext as _

from open_municipio.filters import OMByFieldDistinctFilter
from open_municipio.newscache.models import *

class GeneratingCTFilter(OMByFieldDistinctFilter):

    model = News
    field = 'generating_content_type'
    field_label = 'generating_content_type__name'
    title = _("generating content type")


class RelatedCTFilter(OMByFieldDistinctFilter):

    model = News
    field = 'related_content_type'
    field_label = 'related_content_type__name'
    title = _("related content type")


class NewsAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    list_filter = ('priority', 'news_type', GeneratingCTFilter, RelatedCTFilter)
    
    list_display = ('created_format', 'priority', 'news_type', 'generating_object', 'related_object', 'text')

    def created_format(self, obj):

        return obj.created.strftime("%d/%m/%y %H:%M:%S")
    created_format.admin_order_field = "created"


admin.site.register(News, NewsAdmin)


