from django.conf import settings
from django import forms
from django.utils.encoding import force_unicode

from django.contrib.comments.forms import CommentForm
from django.contrib.contenttypes.models import ContentType

from django.utils.safestring import mark_safe
from open_municipio.om_comments.models import CommentWithMood

import datetime

class HorizontalRadioRenderer(forms.RadioSelect.renderer):
    """ this overrides widget method to put radio buttons horizontally
        instead of vertically.
    """
    def render(self):
        """
        Outputs radios
        """
        return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))

class CommentFormWithMood(CommentForm):
    """
    A comment form which matches the default djanago.contrib.comments
    one, plus a few custom fields.
    """
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
