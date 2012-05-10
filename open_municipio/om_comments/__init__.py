from django.core.urlresolvers import reverse 

from open_municipio.om_comments.models import CommentWithMood
from open_municipio.om_comments.forms import CommentFormWithMood


def get_model():
    return CommentWithMood

def get_form():
    return CommentFormWithMood

def get_form_target():
    """
    Returns the target URL for the comment form submission view.
    """
    return reverse('comments-post-comment')