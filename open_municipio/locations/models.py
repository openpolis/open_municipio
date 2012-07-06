from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch.dispatcher import receiver
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User
from open_municipio.monitoring.models import MonitorizedItem

from open_municipio.om_utils.models import SlugModel



class Location(SlugModel, MonitorizedItem):
    """
    A concise description of a town's location.
    
    ``Location`` instances may be used as labels to provide a geographic-aware taxonomy 
    for content objects (particularly, ``Act`` instances).       
    """
    name = models.CharField(verbose_name=_('Name'), max_length=100)
    address = models.CharField(verbose_name=_('Address'), max_length=100, blank=True)
    # FIXME: choose the right number of significant digits
    latitude = models.FloatField(verbose_name=_('Latitude'), blank=True, null=True)
    # FIXME: choose the right number of significant digits
    longitude = models.FloatField(verbose_name=_('Longitude'), blank=True, null=True)

    # cached value of how many act uses it
    count = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = _('location')
        verbose_name_plural = _('locations')
    
    def __unicode__(self):
        return u'%s' % self.name
        
    @property
    def acts(self):
        """
        Returns the ``QuerySet`` of all acts tagged with this location.  
        """
        return self.tagged_act_set.all()

    @models.permalink
    def get_absolute_url(self):
        return 'om_location_detail', (), { 'slug': self.slug }
    
    
class TaggedActByLocation(models.Model):
    """
    A intermediate model to record associations between locations and acts.
    
    Beyond the act being tagged and the location being associated to it, 
    a few tagging metadata are also recorded:
    
    * ``tagger``: the user (an ``auth.User`` instance) who tagged the act
    * ``tagging_time``: a timestamp specifying when the act was tagged
    
    """
    act = models.ForeignKey('acts.Act')
    location = models.ForeignKey(Location, related_name='tagged_act_set')
    tagger = models.ForeignKey(User, null=True, blank=True, editable=False)
    tagging_time = models.DateTimeField(null=True, auto_now_add=True, editable=False)
                                       
    class Meta:
        verbose_name = _("tagged act by location")
        verbose_name_plural = _("tagged acts by location")
        
    def __unicode__(self):
        params = {
                  'tagger': self.tagger, 
                  'location': self.location,
                  'act_id': self.act.pk,
                  'time': self.tagging_time,
                  }
        return u"User '%(tagger)s' added location '%(location)s' to act #%(act_id)s at %(time)s" % params

def reset_location_counters():
    for item in Location.objects.all():
        item.count = TaggedActByLocation.objects.filter(location=item).count()
        item.save()

def locations_tagging_stats():
    print "------\nTAGGING STATS:\n"
    print "Locations: \n"
    print [("%s[%s]" % (x, x.count)) for x in Location.objects.all()]
    print "\n-----"


@receiver(post_save, sender=TaggedActByLocation)
def new_tagging_by_location(**kwargs):
    """
    Increment counter of related location
    """
    if not kwargs.get('raw', False) and kwargs.get('created', False):
        tagging = kwargs.get('instance')
        tagging.location.count += 1
        tagging.location.save()

@receiver(pre_delete, sender=TaggedActByLocation)
def remove_tagging_by_location(**kwargs):
    """
    Decrement counter of related location
    """
    tagging = kwargs.get('instance')
    tagging.location.count = max(0, tagging.location.count - 1)
    tagging.location.save()