from django.db import models
from django.contrib.comments.models import Comment
from django.contrib.auth.models import User
from django.utils.translation import ugettext, ugettext_lazy as _

COMMENT_MOOD = (
    ('+', _('Positive')),
    ('-', _('Negative')),
    ('0', _('Neutral')),
    )

class CommentWithMood(Comment):
    mood = models.CharField(_("Comment mood"), max_length=1, choices=COMMENT_MOOD, default="0")
    open_municipio_user = models.ForeignKey(User, blank=True, null=True)

    class Meta:
        verbose_name = "Comment"
