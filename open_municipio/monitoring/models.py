from django.db import models
from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User

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
                                       related_name="%(class)s_monitoring")
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
