from django.conf import settings
from django import forms
from django.utils.encoding import force_unicode

from django.contrib.comments.forms import CommentForm
from django.contrib.contenttypes.models import ContentType

from open_municipio.om_utils.widgets import HorizontalRadioRenderer
from open_municipio.om_comments.models import CommentWithMood

import datetime
import sys
from haystack.forms import SearchForm

from open_municipio.om_search.forms import RangeFacetedSearchForm

class CommentSearchForm(RangeFacetedSearchForm):

    def __init__(self, *args, **kwargs):
        super(CommentSearchForm, self).__init__(*args, **kwargs)

    def search(self):
        sqs = super(CommentSearchForm, self).search()

        # default sorting
        if (self.is_valid() and not self.cleaned_data.get('order_by')) or not self.is_valid():
            sqs = sqs.order_by('-date')

        return sqs


class CommentFormWithMood(CommentForm):
    """
    A custom comment form, adding a ``mood`` field to the built-in form
    provided by ``django.contrib.comments``.
    """
    # FIXME: this class should inherit from ``CommentSecurityForm``, a subclass of ``CommentDetailsForm``
    # see: https://docs.djangoproject.com/en/1.3/ref/contrib/comments/forms/#abstract-comment-forms-for-custom-comment-apps
    mood = forms.ChoiceField(widget=forms.widgets.RadioSelect(renderer=HorizontalRadioRenderer), 
                             choices=CommentWithMood.MOOD_CHOICES, 
                             initial=CommentWithMood.NEUTRAL)
    
    def get_comment_model(self):
        # Use our custom comment model instead of the built-in one.
        return CommentWithMood

    def get_comment_create_data(self):
        # Use the data of the superclass, and customize fields
        return dict(
            content_type = ContentType.objects.get_for_model(self.target_object),
            object_pk    = force_unicode(self.target_object.pk),
            comment      = self.cleaned_data["comment"],
            submit_date  = datetime.datetime.now(),
            site_id      = settings.SITE_ID,
            is_public    = True,
            is_removed   = False,
            mood         = self.cleaned_data['mood'],
            )
