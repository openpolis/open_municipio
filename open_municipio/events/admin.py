from django.contrib import admin
from django.forms import ModelForm, CharField
from open_municipio.events.models import *
from tinymce.widgets import TinyMCE


class EventForm(ModelForm):
    description = CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 25}))
    class Meta:
        model = Event

class EventAdmin(admin.ModelAdmin):
    filter_horizontal = ('acts',)
    form = EventForm

admin.site.register(Event, EventAdmin)

