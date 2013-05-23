from django.contrib import admin 
from django.utils.translation import ugettext_lazy as _
from open_municipio.taxonomy.models import Category, Tag


class TagInCategoryInline(admin.TabularInline):
    model = Category.tag_set.through

class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'count')

    inlines = [ TagInCategoryInline, ]

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'count')
    fields = ('name', 'slug', 'tag_set', )
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)

