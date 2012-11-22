from django.db import models

from datetime import datetime, timedelta

# Events are shown in templates through a calendar widget. Events in
# the past are shown up to EVENTS_DAYS_IN_THE_PAST days ago.
EVENTS_DAYS_IN_THE_PAST = 0


class EventManager(models.Manager):
    def get_query_set(self):
        """
        Custom manager to filter remote past events away
        """
        now = datetime.now()
        start_date = now - timedelta(days=EVENTS_DAYS_IN_THE_PAST)
        return super(EventManager, self).get_query_set().filter(date__gt=start_date)
