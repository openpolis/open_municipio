from django.db import models
from django.core.urlresolvers import reverse 
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User

class Monitoring(models.Model):
    """
    This model maps the monitoring of a content object by a user.
    
    This monitoring relation is *polymorphic* (generic),
    i.e. every content type may be monitored by a given user.
    
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
