from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.comments.admin import CommentsAdmin

from open_municipio.om_comments.models import CommentWithMood

class CommentWithMoodAdmin(CommentsAdmin):
    pass

# A try/except wrapper is necessary here to prevent this class from
# being unregistered more than once, which would lead to errors. Those
# multiple unregister attempts are probably due to circular imports
# (``from django.contrib.comments.admin import CommentsAdmin``).
try:
    admin.site.unregister(CommentWithMood)
except NotRegistered:
    pass

admin.site.register(CommentWithMood, CommentWithMoodAdmin)

