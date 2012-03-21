from django.db import models
from django.utils.translation import ugettext_lazy as _

from open_municipio.acts.models import Act
from open_municipio.events.managers import EventManager
from open_municipio.people.models import Institution

from datetime import datetime


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

