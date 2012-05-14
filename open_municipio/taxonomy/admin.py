from django.contrib import admin 
from django.utils.translation import ugettext_lazy as _
from open_municipio.taxonomy.models import Category, Tag


class CategoryAdmin(admin.ModelAdmin):
    fields = ('name', 'slug')
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag)

