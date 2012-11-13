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


#
# Signals handlers
#

@receiver(post_save, sender=CommentWithMood)
@receiver(post_save, sender=Vote)
def new_user_activity(sender, **kwargs):
    """
    Generates a record in the newscache, when a user activity happens. 
    
    User activities include:
    
    * users casting votes upon an object
    * users commenting an object
    """
    raw_mode = kwargs['raw']
    created = kwargs['created'] 
    # the object (vote or comment) which generates the news item(s) 
    generating_object = kwargs['instance']
    # generate news only if not in raw mode (fixtures)
    # and when a new object (comment or vote) has been saved to the DB
    if not raw_mode and created:
        if sender == Vote: # new vote
            vote = generating_object
            content_object = vote.object
            user = vote.user.get_profile()
            prefix = 'comment'
        elif sender == CommentWithMood: # new comment            
            comment = generating_object
            content_object = comment.content_object
            user = comment.user.get_profile()
            prefix = 'vot'
        # build a context for generating a textual representation of the news
        ctx = Context({ 'object': content_object, 'user': user })

        ## Two news items are generated

        ## the first news item is related to the object being voted/commented, 
        ## and generated only once a day, when that object has been voted/commented for the first time

        # get today's datetime, at midnight
        t = datetime.datetime.today()
        d = datetime.datetime(year=t.year, month=t.month, day=t.day)

        # retrieve the ``DateQuerySet`` of all days during which at least one news item 
        # related to the content object at hand has been generated
        day_qs = News.objects.filter(
            generating_content_type=ContentType.objects.get_for_model(generating_object),
            related_content_type=ContentType.objects.get_for_model(content_object),
            related_object_pk=content_object.pk
        ).dates('created', 'day')

        # generate a news item only if no other news items were already generated today
        if d not in day_qs:
            News.objects.create(
                generating_object=generating_object, related_object=content_object,
                priority=2, news_type=News.NEWS_TYPE.community,
                text=News.get_text_for_news(ctx, 'newscache/object_%sed.html' % prefix)
            )

        ## the second news item is related to the commenting/voting user, with priority 2
        News.objects.create(
            generating_object=generating_object, related_object=user,
            priority=2, news_type=News.NEWS_TYPE.community,
            text=News.get_text_for_news(ctx, 'newscache/user_%sing.html' % prefix)
        )


@receiver(pre_delete, sender=CommentWithMood)
@receiver(pre_delete, sender=Vote)
def removed_comment_or_vote(sender, **kwargs):
    """
    When a user revokes either a vote or a comment on a given content object, 
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