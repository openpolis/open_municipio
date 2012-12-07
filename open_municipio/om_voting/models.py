import datetime
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, pre_delete
from django.dispatch.dispatcher import receiver
from django.template import Context
from voting.models import Vote

#
# Signals handlers
#
from open_municipio.newscache.models import News

@receiver(post_save, sender=Vote)
def new_user_activity(sender, **kwargs):
    """
    Generates a record in the newscache, when a user votes an item.
    """
    raw_mode = kwargs['raw']
    created = kwargs['created']
    # the object (vote or comment) which generates the news item(s)
    generating_object = kwargs['instance']
    # generate news only if not in raw mode (fixtures)
    # and when a new object (comment or vote) has been saved to the DB
    if not raw_mode and created:
        vote = generating_object
        content_object = vote.object
        user = vote.user.get_profile()
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
        # removed 07/12/2012, always generates news, uncomment to change behavior
        # if d not in day_qs
        News.objects.create(
            generating_object=generating_object, related_object=content_object,
            priority=1, news_type=News.NEWS_TYPE.community,
            text=News.get_text_for_news(ctx, 'newscache/object_voted.html')
        )

        ## the second news item is related to the commenting/voting user, with priority 3
        News.objects.create(
            generating_object=generating_object, related_object=user,
            priority=3, news_type=News.NEWS_TYPE.community,
            text=News.get_text_for_news(ctx, 'newscache/user_voting.html')
        )


@receiver(pre_delete, sender=Vote)
def removed_comment_or_vote(sender, **kwargs):
    """
    When a user revokes either a vote or a comment on a given content object,
    delete the corresponding record(s) from the newscache.
    """
    generating_object = kwargs['instance']

    vote = generating_object
    content_object = vote.object
    user = vote.user.get_profile()

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