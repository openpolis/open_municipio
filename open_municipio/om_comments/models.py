from django.contrib.comments.models import Comment
from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _


class CommentWithMood(Comment):
    POSITIVE = '+'
    NEGATIVE = '-'
    NEUTRAL = '0'
    MOOD_CHOICES = (
        (POSITIVE, _('Positive')),
        (NEGATIVE, _('Negative')),
        (NEUTRAL, _('Neutral')),                      
    )
    
    mood = models.CharField(_("Comment mood"), max_length=1, choices=MOOD_CHOICES, default=NEUTRAL)    

    class Meta:
        verbose_name = "Comment"
