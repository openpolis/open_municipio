from django.contrib import admin

from open_municipio.speech.models import Speech, SpeechAttachment
from open_municipio.speech.forms import SpeechAdminForm
from open_municipio.speech.filters import IsPublicFilter

class SpeechAttachmentInline(admin.StackedInline):
    model = SpeechAttachment
    extra = 0

class SpeechAdmin(admin.ModelAdmin):
    form = SpeechAdminForm
    raw_id_fields = ( "act", "speaker", )
    list_display = ("date", "speaker", "title","act_title_cut","is_public")
    list_filter = (IsPublicFilter, )

    def change_view(self, request, object_id, form_url='', extra_content=None):
        if request.user.is_superuser:
            self.inlines = [SpeechAttachmentInline]

        self.inline_instances = []
        for inline_class in self.inlines:
            inline_instance = inline_class(self.model, self.admin_site)
            self.inline_instances.append(inline_instance)
        
        return super(SpeechAdmin, self).change_view(request, object_id, \
            form_url, extra_content)


admin.site.register(Speech, SpeechAdmin)
admin.site.register(SpeechAttachment)
