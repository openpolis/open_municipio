from django.contrib import admin
from django.forms import ModelForm, CharField
from open_municipio.events.models import *
from tinymce.widgets import TinyMCE


class EventForm(ModelForm):
    description = CharField(widget=TinyMCE(
        attrs={'cols': 80, 'rows': 25},
        mce_attrs={
            'theme': "advanced",
            'theme_advanced_buttons1': "formatselect,bold,italic,underline|,bullist,numlist,|,undo,redo,|,link,unlink,|,code,help",
            'theme_advanced_buttons2': "",
            'theme_advanced_buttons3': "",
            'theme_advanced_blockformats': "p,blockquote",
            'theme_advanced_resizing': True,
            'theme_advanced_statusbar_location': "bottom",
            'theme_advanced_toolbar_location': "top",
            'theme_advanced_path': False
        }
    ))
    class Meta:
        model = Event

class EventAdmin(admin.ModelAdmin):
    filter_horizontal = ('acts',)
    form = EventForm

admin.site.register(Event, EventAdmin)

