from django.db import models
from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.context import Context
from open_municipio.newscache.models import News

class Monitoring(models.Model):
    """
    The class that maps the monitoring of an object by a user.
    The relation to the object is polimorphic (generic).
    
    An example of a user monitoring an object::
    
        a = Act.objects.get(pk=3)
        u = User.objects.get(username='guglielmo')
        m = Monitoring(content_object=a, user=u)
        m.save()
 
    """
    
    # What's being monitored
    content_type   = models.ForeignKey(ContentType,
                                       verbose_name=_('content type'),
                                       related_name="content_type_set_for_%(class)s")
    object_pk      = models.PositiveIntegerField(_('object ID'))
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")
    
    # Who's monitoring
    user           = models.ForeignKey(User, verbose_name=_('user'),
                                       related_name="%(class)ss")
    # Is it a public monitoring (visibility)
    # defaults to true
    is_public      = models.BooleanField(default=True)
    
    # When monitoring started (auto-filled at save, when new)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return u'user %s is monitoring %s from %s' % (self.user, self.content_object, self.created_at)

    def get_content_object_url(self):
        """
        Get a URL suitable for redirecting to the content object.
        """
        return urlresolvers.reverse(
            "monitoring-url-redirect",
            args=(self.content_type_id, self.object_pk)
        )


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
        monitoring_user = generating_item.user
        # define context for textual representation of the news
        ctx = Context({ 'monitored_object': monitored_object, 'monitoring_user': monitoring_user })

        # two news are generated

        # first news related to the monitored object, with priority 3
        News.objects.create(
            generating_object=generating_item, related_object=monitored_object,
            priority=3, news_type=News.NEWS_TYPE.community,
            text=News.get_text_for_news(ctx, 'newscache/object_monitored.html')
        )
        # second news related to the monitoring user, with priority 2
        News.objects.create(
            generating_object=generating_item, related_object=monitoring_user,
            priority=2, news_type=News.NEWS_TYPE.community,
            text=News.get_text_for_news(ctx, 'newscache/user_monitoring.html')
        )
