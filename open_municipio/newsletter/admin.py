from django.contrib import admin
from open_municipio.newsletter.models import *


class NewsletterAdmin(admin.ModelAdmin):
    readonly_fields = ['started', 'finished']

admin.site.register(Newsletter, NewsletterAdmin)
