from django.db import models
from django.utils.translation import ugettext_lazy as _

from open_municipio.people.models import Institution
from open_municipio.acts.models import Act

from datetime import datetime

#
# Events
#

class EventManager(models.Manager):
    def get_query_set(self):
        """
        Custom manager to filter past events away
        """
        now = datetime.now()
        return super(EventManager, self).get_query_set().filter(date__gt=now)

    def get_by_act(self, act):
        """
        Returns future events regarding a specific act
        """
        return self.get_query_set().filter(act__pk=act)
        
    def get_by_institution(self, institution):
        """
        Returns future events regarding a specific institution
        """
        return self.get_query_set().filter(institution__pk=institution)
        
    #FIXME: this is just a stub
    def get_by_category(self, category):
        """
        Returns future events regarding acts under a specific category
        """
        return self.get_query_set().filter(act__category=category)
        
    #FIXME: this is just a stub
    def get_by_tag(self, tag):
        """
        Returns future events regarding acts under a specific tag
        """
        return self.get_query_set().filter(act__tag=tag)
        
    #FIXME: this is just a stub
    def get_by_politician(self, politician):
        """
        Returns future events regarding acts signed by a specific
        politician
        """
        return self.get_query_set().filter(act__politician=politician)



class Event(models.Model):
    """
    This class allows OpenMunicipio site to keep track of upcoming
    events.

    Fields:

    * A datefield, no time is needed

    * A foreign key to the ``Institution`` that will "host" the event;
      eg: council or city government

    * A foreign key to the involved ``Act``

    * A textfield for some description

    Since we will always be interested in future events (with regard
    to current date), a custom model manager is provided that allows
    ``Event.future.all()``.
    """

    date = models.DateField(_("Event date"))
    institution = models.ForeignKey(Institution)
    act = models.ForeignKey(Act, blank=True, null=True)
    description = models.TextField(_("Description"), max_length=500, blank=True, null=True)

    # The default manager
    objects = models.Manager()
    # Future events will be retrieved using ``Event.future.all()``
    future = EventManager()

    def __unicode__(self):
        uc = u'%s - %s' % (self.date, self.act)
        return uc

