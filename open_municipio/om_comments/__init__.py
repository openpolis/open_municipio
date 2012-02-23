from open_municipio.om_comments.models import CommentWithMood
from open_municipio.om_comments.forms import CommentFormWithMood


def get_model():
    return CommentWithMood

def get_form():
    return CommentFormWithMood
