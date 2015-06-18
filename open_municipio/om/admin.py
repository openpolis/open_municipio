from django.utils.safestring import mark_safe
from django.contrib import admin
from django.core.urlresolvers import reverse

class LinkedTabularInline(admin.TabularInline):

    def admin_link(self, instance):
        if instance.id is None:
            return ""
        
        url = reverse('admin:%s_%s_change' % (
            instance._meta.app_label,  instance._meta.module_name), \
                      args=[instance.id] )
        return mark_safe(u'<a href="{u}">Edit</a>'.format(u=url))

    readonly_fields = ('admin_link',)