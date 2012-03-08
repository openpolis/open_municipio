from django.db.models import Q
from django.db.models.query import QuerySet

from datetime import datetime

class TimeFramedQuerySet(QuerySet):
    """
    A custom ``QuerySet`` allowing easy retrieval of current, past and future instances 
    of a timeframed model.
    
    Here, a *timeframed model* denotes a model class having an associated time range.
    
    We assume that the time range is described by two ``Date`` (or ``DateTime``) fields
    named ``start_date`` and ``end_date``, respectively.
    """
    def current(self):
        """
        Return a QuerySet containing the *current* instances of the model 
        (i.e. those for which the current date-time lies within their associated time range). 
        """
        now = datetime.now()
        return self.filter(Q(start_date__lte=now) & 
                           (Q(end_date__gte=now) | Q(end_date__isnull=True)))
        
    def past(self):
        """
        Return a QuerySet containing the *past* instances of the model
        (i.e. those having an end date which is in the past).
        """
        now = datetime.now()
        return self.filter(end_date__lte=now)
    
    def future(self):
        """
        Return a QuerySet containing the *future* instances of the model
        (i.e. those having a start date which is in the future).
        """
        now = datetime.now()
        return self.filter(start_date__gte=now)