from django.contrib import admin
from django.forms import ModelForm, CharField
from open_municipio.events.models import *
from tinymce.widgets import TinyMCE

from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.forms import Textarea, ModelForm, TextInput

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

class EventActInlineForm(ModelForm):
    class Meta:
        widgets = {
            'order' : TextInput(attrs={'readonly':'readonly', 'class':'sortable'})

        }

#class EventActInlineFormSet(BaseInlineFormSet):
#
#    def add_fields(self, form, index):
#        print "ding"
#        super(EventActInlineFormSet,self).add_fields(form, index)
#        print index
#

class EventActInline(admin.TabularInline):
    form = EventActInlineForm
#    formset = EventActInlineFormSet
    model = EventAct
    extra = 0

#    def __init__(self, *args, **kwargs):
#        print "form personalizzato..."
#        return super(self.__class__,self).__init__(*args,**kwargs)
#
#    def formfield_for_dbfield(self, db_field, **kwargs):
#        print "chiamato form_field_for_dbfield %s" % db_field
#        return super(self.__class__,self).formfield_for_dbfield(db_field,
#            **kwargs)

class EventAdmin(admin.ModelAdmin):
    filter_horizontal = ('acts',)
    form = EventForm
    inlines = [ EventActInline, ]
    

admin.site.register(Event, EventAdmin)

