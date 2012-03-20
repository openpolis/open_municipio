from django.db import models

from datetime import datetime


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
        return self.get_query_set().filter(act__pk=act.pk)
        
    def get_by_institution(self, institution):
        """
        Returns future events regarding a specific institution
        """
        return self.get_query_set().filter(institution__pk=institution.pk)
        
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
