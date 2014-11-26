from django.db import models
from django.core.urlresolvers import reverse 
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.template.context import Context
from open_municipio.newscache.models import News

class Monitoring(models.Model):
    """
    This model maps the monitoring of a content object by a user.
    
    This monitoring relation is *polymorphic* (generic),
    i.e. every content type may be monitored by a given user.
    
    An example of a user monitoring an object::
    
        a = Act.objects.select_subclasses().get(pk=3)
        u = User.objects.get(username='guglielmo')
        m = Monitoring(content_object=a, user=u)
        m.save()

    It is important, for acts, to be sure that acts be downcasted before being
    referenced. The object being monitored MUST be the Deliberation,
    not the superclass (Act) instance.
    """
    
    # What's being monitored
    content_type   = models.ForeignKey(ContentType,
                                       verbose_name=_('content type'),
                                       related_name="content_type_set_for_%(class)s")
    object_pk      = models.PositiveIntegerField(_('object ID'))
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")
    
    # Who's monitoring
    user           = models.ForeignKey(User, verbose_name=_('user'),
                                       related_name="%(class)s_set")
    # Is it a public monitoring ? (visibility)
    # defaults to True
    is_public      = models.BooleanField(default=True)
    
    # When monitoring started (auto-set at the current datetime, on creation)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return u'user %s is monitoring %s since %s' % (self.user, self.content_object, self.created_at)

    def get_content_object_url(self):
        """
        Get a URL suitable for redirecting to the content object.
        """
        return reverse('om_monitoring_url_redirect', args=(), kwargs=(self.content_type.pk, self.object_pk))


class MonitorizedItem():



    def monitorings(self, user_type=None):
        """
        Returns the list of monitorings for this act.

        user_type can take None, "simple", "politician" and indicates whether to apply a filter

        """
        try:
            type = ContentType.objects.get_for_model(self.downcast())
        except AttributeError:
            type = ContentType.objects.get_for_model(self)

        if user_type == "simple":
            return Monitoring.objects.filter(content_type__pk=type.id, object_pk=self.pk, user__userprofile__person__isnull=True)
            #return self.monitoring_set.filter(user__userprofile__person__isnull=True)
        elif user_type == "politician":
            return Monitoring.objects.filter(content_type__pk=type.id, object_pk=self.pk, user__userprofile__person__isnull=False)
            #return self.monitoring_set.filter(user__userprofile__person__isnull=False)
        else:
            return Monitoring.objects.filter(content_type__pk=type.id, object_pk=self.pk,)
            #return self.monitoring_set.all()

    @property
    def all_monitoring_users(self):
        # FIXME: This method should return a QuerySet for efficiency reasons
        # (an act could be monitored by a large number of people;
        # moreover, often we are only interested in the total number of
        # monitoring users, so building a list in memory may result in a waste of resources).
        return [m.user for m in self.monitorings()]

    @property
    def all_monitoring_count(self):
        return self.monitorings().count()

    @property
    def monitoring_users(self):
        """
        Returns the list of users monitoring this argument (category).
        """
        # FIXME: This method should return a QuerySet for efficiency reasons
        # (an act could be monitored by a large number of people;
        # moreover, often we are only interested in the total number of
        # monitoring users, so building a list in memory may result in a waste of resources).
        return [m.user for m in self.monitorings(user_type='simple')]

    @property
    def monitoring_users_count(self):
        return self.monitorings(user_type='simple').count()

    @property
    def monitoring_politicians(self):
        # FIXME: This method should return a QuerySet for efficiency reasons
        # (an act could be monitored by a large number of people;
        # moreover, often we are only interested in the total number of
        # monitoring users, so building a list in memory may result in a waste of resources).
        return [m.user for m in self.monitorings(user_type='politician')]

    @property
    def monitoring_politicians_count(self):
        return self.monitorings(user_type='politician').count()

    @property
    def content_type_id(self):
        """
        Returns id of the content type associated with this instance.
        """
        return ContentType.objects.get_for_model(self).id

#
# Signals handlers
#

@receiver(post_save, sender=Monitoring)
def new_monitoring(**kwargs):
    """
    generates a record in newscache, when someone starts monitoring something
    """
    # generates news only if not in raw mode (fixtures)
    # and for objects creation
    if not kwargs.get('raw', False) and kwargs.get('created', False):
        generating_item = kwargs['instance']
        monitored_object = generating_item.content_object
        monitoring_user = generating_item.user.get_profile()
        # define context for textual representation of the news
        ctx = Context({ 'monitored_object': monitored_object, 'monitoring_user': monitoring_user })

        # two news are generated

        # first news related to the monitored object, with priority 2 (home)
        # User X has started to monitor item Y
        News.objects.create(
            generating_object=generating_item, related_object=monitored_object,
            priority=2, news_type=News.NEWS_TYPE.community,
            text=News.get_text_for_news(ctx, 'newscache/object_monitored.html')
        )
        # second news related to the monitoring user, with priority 3 (user's page)
        # This user has started to monitor item Y
        News.objects.create(
            generating_object=generating_item, related_object=monitoring_user,
            priority=3, news_type=News.NEWS_TYPE.community,
            text=News.get_text_for_news(ctx, 'newscache/user_monitoring.html')
        )


@receiver(pre_delete, sender=Monitoring)
def remove_monitoring(**kwargs):
    """
    removes records in newscache, when someone stops monitoring something
    """
    generating_item = kwargs['instance']
    monitored_object = generating_item.content_object
    monitoring_user = generating_item.user.get_profile()

    if not generating_item:
        return

    if monitored_object:
        # remove news related to the monitored object
        News.objects.filter(
            generating_content_type=ContentType.objects.get_for_model(generating_item),
            generating_object_pk = generating_item.pk,
            related_content_type=ContentType.objects.get_for_model(monitored_object),
            related_object_pk=monitored_object.pk
        ).delete()

    if monitoring_user:
        # remove news related to the monitoring user
        News.objects.filter(
            generating_content_type=ContentType.objects.get_for_model(generating_item),
            generating_object_pk = generating_item.pk,
            related_content_type=ContentType.objects.get_for_model(monitoring_user),
            related_object_pk=monitoring_user.pk
        ).delete()
