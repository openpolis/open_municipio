from django.contrib import admin
from django.forms import ModelForm, CharField
from django.utils.translation import ugettext_lazy as _
from tinymce.widgets import TinyMCE
from open_municipio.idioticon.models import Term


class TermForm(ModelForm):
    definition = CharField(
        label=_('Definition'),
        widget=TinyMCE(
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
        )
    )
    class Meta:
        model = Term

class TermAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("term",)}
    form = TermForm

admin.site.register(Term, TermAdmin)
