from django import template
from django.conf import settings
from django.contrib import comments
from django.contrib.auth.decorators import login_required
from django.contrib.comments.models import Comment
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect

import datetime


# Number of minutes within users can delete their own comments
MAX_TIME_FOR_COMMENT_REMOVAL = 10

@login_required
def delete_own_comment(request, message_id):
    """
    Users can delete their own comments within a certain time lapse.
    """

    now = datetime.datetime.now()
    control_date = now - datetime.timedelta(minutes=MAX_TIME_FOR_COMMENT_REMOVAL)

    # I retrieve the comment if it's been written in the past few
    # minutes: ``submit_date__gte=control_date``
    comment = get_object_or_404(comments.get_model(), pk=message_id,
                                site__pk=settings.SITE_ID,
                                submit_date__gte=control_date)

    # Does current user really own it?
    if (comment.user == request.user):
        # Then flag it as removed!
        comment.is_removed = True
        comment.save()

    # Whatever happened, just get back to the act page
    return redirect('act-detail', comment.content_object.id)
