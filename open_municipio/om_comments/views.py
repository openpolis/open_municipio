from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.http import HttpResponseRedirect 
from django.shortcuts import get_object_or_404

from django.contrib import comments

from django.contrib.auth.decorators import login_required

from voting.views import RecordVoteOnItemView

from open_municipio.om_comments.models import CommentWithMood

import datetime



class DeleteOwnCommentView(View):
    """
    Users can delete their own comments within a certain time lapse.
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteOwnCommentView, self).dispatch(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):    
        now = datetime.datetime.now()
        control_date = now - datetime.timedelta(seconds=settings.OM_COMMENTS_REMOVAL_MAX_TIME)
        # retrieve the comment that has been asked for removal
        comment = get_object_or_404(comments.get_model(), pk=self.kwargs.get('pk', None))
        # check if the comment may be removed, i.e if all the following conditions hold true:
        # * it was posted by the same user who made the removal request
        # * it belongs to the current site
        # * the time thresold for removal has not expired, yet 
        if (comment.user == request.user) and (comment.site.pk == settings.SITE_ID) and (comment.submit_date >= control_date):    
            # flag the comment as removed!
            comment.is_removed = True
            comment.save()
  
        # Whatever happened, just get back to the detail page of the content object the comment is attached to
        return HttpResponseRedirect(comment.content_object.get_absolute_url())
    

class RecordVoteOnCommentView(RecordVoteOnItemView):
    model = CommentWithMood  