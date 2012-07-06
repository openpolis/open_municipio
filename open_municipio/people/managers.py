from django.db.models import Q
from django.db.models.query import QuerySet

from datetime import datetime

class TimeFramedQuerySet(QuerySet):
    """
    A custom ``QuerySet`` allowing easy retrieval of current, past and future instances 
    of a timeframed model.
    
    Here, a *timeframed model* denotes a model class having an associated time range.
    
    We assume that this time range is implemented as two ``Date`` (or ``DateTime``) fields
    named ``start_date`` and ``end_date``, respectively.
    """
    # FIXME: this manager is rather generic, so it should be moved 
    # under either the ``om`` or ``om_utils`` application
    def past(self):
        """
        Return a queryset containing *past* instances of the model
        (i.e. those having an end date which is in the past).
        """
        now = datetime.now()
        return self.filter(end_date__lte=now)
    
    def future(self):
        """
        Return a queryset containing *future* instances of the model
        (i.e. those having a start date which is in the future).
        """
        now = datetime.now()
        return self.filter(start_date__gte=now)

    def current(self, as_of=None):
        """
        Return a queryset containing model instances which was *current* 
        at a given point in time (as specified by the ``as_of`` argument).
        
        The ``as_of`` argument, if provided, should be a Python datetime object, 
        defaulting to the current date/time.
        """
        time = as_of or datetime.now()
        return self.filter(Q(start_date__lte=time) &
                           Q(end_date__gte=time) | Q(end_date__isnull=True))
