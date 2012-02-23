from django import template
from django.conf import settings
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import comments
from django.contrib.comments import signals
from django.views.decorators.csrf import csrf_protect

from datetime import timedelta
from django.http import Http404


def delete_own_comment(request, comment_id, next=None):
    """
    Users may delete their own comments within a certain time lapse
    from publication.
    """
    print "meow"
    comment = get_object_or_404(comments.get_model(), pk=comment_id, site__pk=settings.SITE_ID)

    now = datetime.now()
    submit_date = comment.submit_date
    max_delta = timedelta(minutes=settings.COMMENT_DELETE_TIME_LIMIT)

    if now - submit_date > max_delta:
        raise Http404 # FIXME: 404 is not a proper answer here

    # Delete on POST
    if request.method == 'POST':
        print "meow"
        # Flag the comment as deleted instead of actually deleting it.
        perform_delete(request, comment)
        return next_redirect(request.POST.copy(), next, delete_done, c=comment.pk)

    # Render a form on GET
    else:
        return render_to_response('comments/delete.html',
            {'comment': comment, "next": next},
            template.RequestContext(request)
        )
