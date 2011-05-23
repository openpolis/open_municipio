from django.contrib import admin 
from om.models import Atto, TipoAtto, Allegato

class AllegatoInline(admin.StackedInline): 
  model = Allegato
  extra = 0

class AttoAdminConAllegati(admin.ModelAdmin):
  inlines = [AllegatoInline]


admin.site.register(Atto, AttoAdminConAllegati)
admin.site.register(TipoAtto)
admin.site.register(Allegato)