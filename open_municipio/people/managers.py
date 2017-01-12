from django.db.models import Q, Count
from django.db.models.query import QuerySet

from datetime import datetime

class TimeFramedQuerySet(QuerySet):
    """
    A custom ``QuerySet`` allowing easy retrieval of current, past and future 
    instances of a timeframed model.
    
    Here, a *timeframed model* denotes a model class having an associated time 
    range.
    
    We assume that the time range is described by two ``Date`` (or 
    ``DateTime``) fields named ``start_date`` and ``end_date``, respectively.
    """
    def past(self, moment=None):
        """
        Return a QuerySet containing the *past* instances of the model
        (i.e. those having an end date which is in the past).
        """
        if moment is None:
            moment = datetime.now()
        elif isinstance(moment, basestring):
            moment = datetime.strptime(moment, "%Y-%m-%d")

        return self.filter(end_date__lte=moment)
    
    def future(self, moment=None):
        """
        Return a QuerySet containing the *future* instances of the model
        (i.e. those having a start date which is in the future).
        """
        if moment is None:
            moment = datetime.now()
        elif isinstance(moment, basestring):
            moment = datetime.strptime(moment, "%Y-%m-%d")

        return self.filter(start_date__gte=moment)

    def current(self, moment=None):
        """
        Return a QuerySet containing the *current* instances of the model
        at the given moment in time, if the parameter is specified
        now if it is not
        @moment - is a datetime, expressed in the YYYY-MM-DD format
        (i.e. those for which the moment date-time lies within their associated time range).
        """
        if moment is None:
            moment = datetime.now()
        elif isinstance(moment, basestring):
            moment = datetime.strptime(moment, "%Y-%m-%d")

        return self.filter(Q(start_date__lte=moment) &
                           (Q(end_date__gte=moment) | Q(end_date__isnull=True)))

class ChargeQuerySet(TimeFramedQuerySet):
        
    def rank_most_acts(self, moment=None):

        if moment is None:
            moment = datetime.today()
        elif isinstance(moment, basestring):
            moment = datetime.strptime(moment, "%Y-%m-%d")

        qs = self.exclude(start_date__gt=moment).exclude(end_date__lt=moment).annotate(n_acts=Count('presented_act_set')).order_by('-n_acts')

        return qs


    def rank_most_interrogations(self, moment=None):

        from open_municipio.acts.models import ActSupport

        if moment is None:
            moment = datetime.today()
        elif isinstance(moment, basestring):
            moment = datetime.strptime(moment, "%Y-%m-%d")

        qs = self.filter(Q(actsupport__act__interrogation__isnull=False) |
            Q(actsupport__act__interpellation__isnull=False) |
            Q(actsupport__act__audit__isnull=False),
            Q(actsupport__support_type=ActSupport.SUPPORT_TYPE.first_signer)).\
            exclude(start_date__gt=moment).exclude(end_date__lt=moment).\
            annotate(n_acts=Count('actsupport')).order_by('-n_acts')

        return qs

    
    def rank_most_rebellious(self, moment=None):

        if moment is None:
            moment = datetime.today()
        elif isinstance(moment, basestring):
            moment = datetime.strptime(moment, "%Y-%m-%d")

        qs = self.extra(select={'perc_rebel':'(n_rebel_votations * 100.0) / GREATEST (n_absent_votations + n_present_votations,1)'}).\
            exclude(start_date__gt=moment).exclude(end_date__lt=moment).\
            order_by('-perc_rebel')
        return qs

    def rank_least_absent(self, moment=None):

        if moment is None:
            moment = datetime.today()
        elif isinstance(moment, basestring):
            moment = datetime.strptime(moment, "%Y-%m-%d")

        qs = self.extra(select={'perc_absences':'(n_absent_votations * 100.0) / GREATEST (n_absent_votations + n_present_votations,1)'}).\
            exclude(start_date__gt=moment).exclude(end_date__lt=moment).\
            order_by('perc_absences')
        return qs

    def rank_most_motions(self, moment=None):

        from open_municipio.acts.models import ActSupport

        if moment is None:
            moment = datetime.today()
        elif isinstance(moment, basestring):
            moment = datetime.strptime(moment, "%Y-%m-%d")


        qs = self.filter(Q(actsupport__act__motion__isnull=False) |
                    Q(actsupport__act__agenda__isnull=False),
                    Q(actsupport__support_type=ActSupport.SUPPORT_TYPE.first_signer)).\
                exclude(start_date__gt=moment).exclude(end_date__lt=moment).\
                annotate(n_acts=Count('actsupport')).order_by('-n_acts')

        return qs





class GroupQuerySet(QuerySet):
   
    def active(self, moment=None):
        """
        An active group is a group that, at a given moment, has charges that
        started before and didn't end or ended later
        """ 

        if moment is None:
            moment = datetime.now()
        elif isinstance(moment, basestring):
            moment = datetime.strptime(moment, "%Y-%m-%d")

        return self.filter(Q(groupcharge__start_date__lte=moment) &
                            (Q(groupcharge__end_date__gte=moment) | 
                                Q(groupcharge__end_date=None))).distinct()
