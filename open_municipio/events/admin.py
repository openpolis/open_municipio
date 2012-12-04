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

class EventActInline(admin.TabularInline):
    form = EventActInlineForm
    model = EventAct
    extra = 0

class EventAdmin(admin.ModelAdmin):
    filter_horizontal = ('acts',)
    form = EventForm
    inlines = [ EventActInline, ]
 
#    def save_form(self, request, form, change):
#        print "ciao3"
#        tmp = super(self.__class__,self).save_form(request, form, change)
#        print "temp %s" % tmp
#        print "temp.acts %s" % tmp.acts.all()
#        return tmp
#
#    def save_model(self, request, obj, form, change):
#        print "ciao2"
#        print "form %s" % form.__class__
#        print "form dict %s" % form.__dict__
##        print "form acts %s" % form.acts
#
##        for curract in form.fields['acts']:
##            print "curr act %s" % curract
#
#        if change:
#            print "num acts delete: %d" % len(obj.acts.all())
#            obj.acts.clear()
#        return super(self.__class__,self).save_model(request, obj, form, change)
#   
#    def save_formset(self, request, form, formset, change):
#        print "ciao"
#        instances = formset.save(commit=False)
#        for instance in instances:
#            # Do something with instance
#            instance.save()
#        formset.save_m2m()
#


admin.site.register(Event, EventAdmin)

