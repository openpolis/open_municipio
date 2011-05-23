from django.contrib import admin 
from opm_site.search.models import SearchKeyword
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.admin import FlatPage

class SearchKeywordAdmin(admin.ModelAdmin): 
  pass

class SearchKeywordInline(admin.StackedInline): 
  model = SearchKeyword

class FlatPageAdminWithKeywords(FlatPageAdmin):
  inlines = [SearchKeywordInline]


admin.site.unregister(FlatPage) 
admin.site.register(FlatPage, FlatPageAdminWithKeywords)
  
admin.site.register(SearchKeyword, SearchKeywordAdmin)