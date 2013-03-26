from django.contrib import admin
from django.forms import ModelForm, CharField
from open_municipio.events.models import *
from tinymce.widgets import TinyMCE

from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.forms import Textarea, ModelForm, TextInput

# TODO place these widget and field in a more reusable location
from open_municipio.speech.widgets import SplitTimeField, SplitTimeWidget

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
        },
    ),
    required=False)
    event_time = SplitTimeField(widget=SplitTimeWidget)

    class Meta:
        model = Event

class EventActInlineForm(ModelForm):
    class Meta:
        widgets = {
            'order' : TextInput(attrs={'readonly':'readonly', 'class':'sortable'})

        }

class EventActInline(admin.TabularInline):
    raw_id_fields = ('act', )
    form = EventActInlineForm
    model = EventAct
    extra = 0

class EventAdmin(admin.ModelAdmin):
    filter_horizontal = ('acts',)
    form = EventForm
    inlines = [ EventActInline, ]
    list_display = [ "title", "date", "institution", ]
    search_fields = [ "title", "institution__name", ]
    list_filter = ("institution", )
 
admin.site.register(Event, EventAdmin)

