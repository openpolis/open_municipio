from django import forms
from django.conf import settings
from django.contrib.comments.forms import CommentForm
from django.contrib.contenttypes.models import ContentType
from django.forms.fields import ChoiceField
from django.forms.widgets import RadioSelect
from django.utils.encoding import force_unicode

from om_comments.models import CommentWithMood, COMMENT_MOOD

import datetime

class CommentFormWithMood(CommentForm):
    """
    A comment form which matches the default djanago.contrib.comments
    one, but with some custom fields.
    """
    mood = forms.ChoiceField(widget=RadioSelect, choices=COMMENT_MOOD, initial="0")

    def get_comment_model(self):
        # Use our custom comment model instead of the built-in one.
        return CommentWithMood

    def get_comment_create_data(self):
        # Use the data of the superclass, and customize fields
        return dict(
            content_type = ContentType.objects.get_for_model(self.target_object),
            object_pk    = force_unicode(self.target_object._get_pk_val()),
            comment      = self.cleaned_data["comment"],
            submit_date  = datetime.datetime.now(),
            site_id      = settings.SITE_ID,
            is_public    = True,
            is_removed   = False,
            mood         = self.cleaned_data['mood'],
            open_municipio_user = None,
            )

CommentFormWithMood.base_fields.pop('name')
CommentFormWithMood.base_fields.pop('email')
CommentFormWithMood.base_fields.pop('url')
