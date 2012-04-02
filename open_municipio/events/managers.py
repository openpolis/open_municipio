from django.db import models

from datetime import datetime, timedelta

# Events are shown in templates through a calendar widget. Events in
# the past are shown up to EVENTS_DAYS_IN_THE_PAST days ago.
EVENTS_DAYS_IN_THE_PAST = 31


class EventManager(models.Manager):
    def get_query_set(self):
        """
        Custom manager to filter remote past events away
        """
        now = datetime.now()
        start_date = now - timedelta(days=EVENTS_DAYS_IN_THE_PAST)
        return super(EventManager, self).get_query_set().filter(date__gt=start_date)

    def get_by_act(self, act):
        """
        Returns events regarding a specific act
        """
        return self.get_query_set().filter(act__pk=act.pk)
        
    def get_by_institution(self, institution):
        """
        Returns events regarding a specific institution
        """
        return self.get_query_set().filter(institution__pk=institution.pk)
        
    #FIXME: this is just a stub
    def get_by_category(self, category):
        """
        Returns events regarding acts under a specific category
        """
        return self.get_query_set().filter(act__category=category)
        
    #FIXME: this is just a stub
    def get_by_tag(self, tag):
        """
        Returns events regarding acts under a specific tag
        """
        return self.get_query_set().filter(act__tag=tag)
        
    #FIXME: this is just a stub
    def get_by_politician(self, politician):
        """
        Returns events regarding acts signed by a specific politician
        """
        return self.get_query_set().filter(act__politician=politician)
