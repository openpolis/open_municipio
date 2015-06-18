from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch.dispatcher import receiver
from django.template.context import Context
from django.utils.translation import ugettext_lazy as _

from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType

from voting.models import Vote

from open_municipio.newscache.models import News

import datetime



class CommentWithMood(Comment):
    POSITIVE = '+'
    NEGATIVE = '-'
    NEUTRAL = '0'
    MOOD_CHOICES = (
        (POSITIVE, _('Positive')),
        (NEGATIVE, _('Negative')),
        (NEUTRAL, _('Neutral')),                      
    )
    
    mood = models.CharField(_("Comment mood"), max_length=1, choices=MOOD_CHOICES, default=NEUTRAL)    

    class Meta:
        verbose_name = "Comment"

    def get_absolute_url(self):
        """
        A comment at the moment is shown in the detail view of its object.
        As a consequence, the comment url is the url of the related object
        """
        return self.content_object.get_absolute_url()


#
# Signals handlers
#

@receiver(post_save, sender=CommentWithMood)
def new_user_activity(sender, **kwargs):
    """
    Generates a record in the newscache, when a user comments an item
    """
    raw_mode = kwargs['raw']
    created = kwargs['created'] 
    # the object (vote or comment) which generates the news item(s) 
    generating_object = kwargs['instance']
    # generate news only if not in raw mode (fixtures)
    # and when a new object (comment or vote) has been saved to the DB
    if not raw_mode and created:
        comment = generating_object
        content_object = comment.content_object
        user = comment.user.get_profile()
        # build a context for generating a textual representation of the news
        ctx = Context({ 'object': content_object, 'commenting_user': user })

        # two news are generated

        # first news related to the commented object, with priority 1 (home)
        # User X has started to monitor item Y
        News.objects.create(
            generating_object=generating_object, related_object=content_object,
            priority=1, news_type=News.NEWS_TYPE.community,
            text=News.get_text_for_news(ctx, 'newscache/object_commented.html')
        )

        ## the second news item is related to the commenting user, with priority 3 (user)
        News.objects.create(
            generating_object=generating_object, related_object=user,
            priority=2, news_type=News.NEWS_TYPE.community,
            text=News.get_text_for_news(ctx, 'newscache/user_commenting.html')
        )


@receiver(pre_delete, sender=CommentWithMood)
def removed_comment_or_vote(sender, **kwargs):
    """
    When a user revokes either a comment on a given content object,
    delete the corresponding record(s) from the newscache.
    """
    generating_object = kwargs['instance']
    
    if sender == Vote: # vote deleted
        vote = generating_object
        content_object = vote.object
        user = vote.user.get_profile()
    elif sender == CommentWithMood: # comment deleted            
        comment = generating_object
        content_object = comment.content_object
        user = comment.user.get_profile()

    # first delete any news item related to the content object
    News.objects.filter(
        generating_content_type=ContentType.objects.get_for_model(generating_object),
        generating_object_pk = generating_object.pk,
        related_content_type=ContentType.objects.get_for_model(content_object),
        related_object_pk=content_object.pk
    ).delete()
    # secondly, delete corresponding, user-related news item(s) 
    News.objects.filter(
        generating_content_type=ContentType.objects.get_for_model(generating_object),
        generating_object_pk = generating_object.pk,
        related_content_type=ContentType.objects.get_for_model(user),
        related_object_pk=user.pk
    ).delete()
