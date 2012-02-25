from django.conf import settings
from django.contrib import comments
from django.contrib.auth.decorators import login_required
from django.contrib.comments.models import Comment
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect

import datetime


# Max time within users can delete their own comments
MAX_TIME_FOR_COMMENT_REMOVAL = datetime.timedelta(minutes=10)

@login_required
def delete_own_comment(request, message_id):
    comment = get_object_or_404(comments.get_model(), pk=message_id,
                                site__pk=settings.SITE_ID)

    submit_date = comment.submit_date
    now = datetime.datetime.now()
    time_elapsed = now - submit_date

    if (time_elapsed < MAX_TIME_FOR_COMMENT_REMOVAL and comment.user == request.user):
        comment.is_removed = True
        comment.save()

    return redirect('act-detail', comment.content_object.id)
