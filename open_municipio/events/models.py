from django.db import models
from django.utils.translation import ugettext_lazy as _

from open_municipio.acts.models import Act
from open_municipio.events.managers import EventManager
from open_municipio.people.models import Institution

from datetime import datetime, date

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

    date = models.DateField(_("Event date"), help_text=_("The day when the event is going to be held"))
    event_time = models.TimeField(_("Event time"), blank=True, null=True, help_text=_("The time of the event"))
    institution = models.ForeignKey(Institution, verbose_name=_("Institution"), help_text=_("The institution that's going to meet during the event"))
    acts = models.ManyToManyField(Act, verbose_name=_("Acts"), blank=True, null=True, help_text=_("Acts the discussion is linked to, if any"),through="EventAct")
    title = models.CharField(_("Title"), max_length=128, blank=True, null=True, help_text=_("A short title for this event"))
    description = models.TextField(_("Description"), blank=True, null=True, help_text=_("A description, containing the list of things that will be discussed during this event"))
    address = models.CharField(_("Address"), max_length=128, blank=True, null=True, help_text=_("The physical address where the meeting is going to be held") )

    # The default manager
    objects = models.Manager()
    # Future events will be retrieved using ``Event.future.all()``
    future = EventManager()

    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')

    def __unicode__(self):
        uc = u'%s %s - %s' % (self.date, self.event_time, self.title)
        return uc

    @property
    def is_past_due(self):
        if date.today() > self.date:
            return True
        return False

class EventAct(models.Model):
    """
    WRITEME
    """
    act = models.ForeignKey(Act)
    event = models.ForeignKey(Event)

    order = models.IntegerField(blank=False,null=False)

    class Meta:
        ordering = ('order',)
        unique_together = ('order','event')
