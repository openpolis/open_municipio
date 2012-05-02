from django.conf.urls.defaults import include, patterns, url

from django.contrib.auth.decorators import login_required
from django.contrib.comments.views.comments import comment_done, post_comment

from open_municipio.om_comments.views import delete_own_comment, RecordVoteOnCommentView



urlpatterns = patterns('',
  # We insert our own post_comment and comment_done urls so to wrap
  # them inside the login_required decorator. We do need that
  # decorator so that only authenticated users can post comments.
  url(r'^post/$', login_required(post_comment), name='comments-post-comment'),
  url(r'^posted/$', login_required(comment_done), name='comments-comment-done'),
  url(r'^delete-own/(\d+)/$', delete_own_comment, name='comments-delete-own-comment'),
  # Users can vote comments
  url(r'^(?P<pk>\d+)/vote/(?P<direction>up|down|clear)/$', RecordVoteOnCommentView.as_view(), name='om_comments_record_user_vote'),
  # Despite the previous urls entries, also standard
  # django.contrib.comments urls must be included. If not, we get some
  # complaints about comment_form_target no reverse match.
  (r'^/', include('django.contrib.comments.urls')),
)
