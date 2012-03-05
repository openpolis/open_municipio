from django.contrib import admin
from django.contrib.comments.admin import CommentsAdmin

from open_municipio.om_comments.models import CommentWithMood

class CommentWithMoodAdmin(CommentsAdmin):
    pass

try:
    admin.site.unregister(CommentWithMood)
except:
    pass

admin.site.register(CommentWithMood, CommentWithMoodAdmin)

