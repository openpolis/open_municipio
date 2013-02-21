from django.contrib import admin

from open_municipio.speeches.models import Speech, SpeechAttachment

class SpeechAttachmentInline(admin.StackedInline):
    model = SpeechAttachment
    extra = 0

class SpeechAdmin(admin.ModelAdmin):
    def change_view(self, request, object_id, extra_content=None):
        if request.user.is_superuser:
            self.inlines = [SpeechAttachmentInline]

        self.inline_instances = []
        for inline_class in self.inlines:
            inline_instance = inline_class(self.model, self.admin_site)
            self.inline_instances.append(inline_instance)
        
        return super(SpeechAdmin, self).change_view(request, object_id, \
            extra_content)

admin.site.register(Speech, SpeechAdmin)
admin.site.register(SpeechAttachment)
