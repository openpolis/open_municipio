import datetime

from django import template
from django.contrib import comments
from django.contrib.comments.models import Comment

from open_municipio.om_comments.views import MAX_TIME_FOR_COMMENT_REMOVAL


register = template.Library()
@register.filter(name='comment_TTL')
def comment_TTL(comment):
    """
    When users post a comment, they are given a certain lapse of time
    to delete it. Given a comment, this filter returns the number of
    seconds the comment is still available for removal.
    """
    max_time = datetime.timedelta(minutes=MAX_TIME_FOR_COMMENT_REMOVAL)
    submit_date = comment.submit_date
    now = datetime.datetime.now()
    TTL = submit_date + max_time - now
    TTL_seconds = int(TTL.total_seconds())

    return max(TTL_seconds, 0)
