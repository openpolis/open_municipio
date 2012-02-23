from django.contrib import admin
from django.contrib.comments.admin import CommentsAdmin

from open_municipio.om_comments.models import CommentWithMood

class CommentWithMoodAdmin(CommentsAdmin):
    pass

# A try/except wrapper is necessary here to prevent this class to be
# unregistered more than once, which would lead to errors. Those
# multiple unregister attempts are probably due to circular imports
# (``from django.contrib.comments.admin import CommentsAdmin``).
try:
    admin.site.unregister(CommentWithMood)
# FIXME: be more specific here (try without the wrapper and see what kind of error is thrown exactly)
except:
    pass

admin.site.register(CommentWithMood, CommentWithMoodAdmin)

