from django.contrib.auth.decorators import login_required
from django.contrib.comments.views import comments

from om_comments.models import CommentWithMood
from om_comments.forms import CommentFormWithMood


original_post_comment = comments.post_comment

@login_required
def post_comment(request, next=None):
    data = request.POST.copy()
    data['open_municipio_user'] = request.user

    return original_post_comment(request, next)

comments.post_comment = post_comment

def get_model():
    return CommentWithMood

def get_form():
    return CommentFormWithMood
