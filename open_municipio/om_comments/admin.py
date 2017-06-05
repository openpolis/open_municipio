from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.comments.admin import CommentsAdmin
from django.forms import ModelForm, CharField

from open_municipio.users.models import UserProfile
from open_municipio.om_comments.models import CommentWithMood

class CommentWithMoodAdminForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(CommentWithMoodAdminForm, self).__init__(*args, **kwargs)
        self.fields["user"].required = True
        self.fields["ip_address"].required = True

    class Meta:
        model = CommentWithMood

class CommentWithMoodAdmin(CommentsAdmin):

    form = CommentWithMoodAdminForm

    def get_form(self, request, obj=None, **kwargs):
        form = super(CommentWithMoodAdmin, self).get_form(request, obj, **kwargs)
        
        default_ip = None
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            default_ip = x_forwarded_for.split(',')[0]
        else:
            default_ip = request.META.get('REMOTE_ADDR')

        default_user = request.user

        default_user_email = default_user.email if default_user else None
        default_username = default_user.username if default_user else None

        default_user_url = None
        try:
            default_user_url = default_user.get_profile().get_absolute_url() 
        except UserProfile.DoesNotExist:
            pass

        form.base_fields["ip_address"].initial = "127.0.0.1"
        form.base_fields["user"].initial = default_user
        form.base_fields["user_name"].initial = default_username
        form.base_fields["user_email"].initial = default_user_email
        form.base_fields["user_url"].initial = default_user_url
        return form
    
# A try/except wrapper is necessary here to prevent this class from
# being unregistered more than once, which would lead to errors. Those
# multiple unregister attempts are probably due to circular imports
# (``from django.contrib.comments.admin import CommentsAdmin``).
try:
    admin.site.unregister(CommentWithMood)
except NotRegistered:
    pass

admin.site.register(CommentWithMood, CommentWithMoodAdmin)

