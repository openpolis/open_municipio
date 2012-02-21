from django.contrib import admin 
from django.utils.translation import ugettext_lazy as _
from open_municipio.taxonomy.models import Category


class CategoryAdmin(admin.ModelAdmin):
    pass

admin.site.register(Category, CategoryAdmin)

