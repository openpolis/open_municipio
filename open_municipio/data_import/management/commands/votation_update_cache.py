import logging

from open_municipio.votations.models import Votation, ChargeVote

from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger("import")

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
    
        for v in Votation.objects.all():

            self.update_cache(v)


    def update_cache(self, v):

        assert isinstance(v, Votation)

        n_yes = ChargeVote.objects.filter(votation=v, vote=ChargeVote.VOTES.yes).count()
        n_no = ChargeVote.objects.filter(votation=v, vote=ChargeVote.VOTES.no).count()
        n_abstained = ChargeVote.objects.filter(votation=v, vote=ChargeVote.VOTES.abstained).count()
        n_secrets = ChargeVote.objects.filter(votation=v, vote=ChargeVote.VOTES.secret).count()
        n_pres = ChargeVote.objects.filter(votation=v, vote=ChargeVote.VOTES.pres).count()
        n_untracked = ChargeVote.objects.filter(votation=v, vote=ChargeVote.VOTES.untracked).count()
        n_absent = ChargeVote.objects.filter(votation=v, vote=ChargeVote.VOTES.absent).count()


        cache_n_presents = n_yes + n_no + n_abstained + n_secrets
        cache_n_partecipants = n_yes + n_no + n_secrets
        cache_n_absents = n_absent + n_untracked
        cache_n_yes = n_yes
        cache_n_no = n_no
        cache_n_abst = n_abstained + n_pres
        
        logger.info("Check cache for votation %s (date: %s, pk: %s)" % (v.idnum, v.sitting.date, v.pk))

        self.update_cache_key("n_presents", cache_n_presents, v)
        self.update_cache_key("n_partecipants", cache_n_partecipants, v)
        self.update_cache_key("n_absents", cache_n_absents, v)
        self.update_cache_key("n_yes", cache_n_yes, v)
        self.update_cache_key("n_no", cache_n_no, v)
        self.update_cache_key("n_abst", cache_n_abst, v)

        v.save()
           
    def update_cache_key(self, key, value, v):
        assert isinstance(key, basestring)
        assert isinstance(value, int)
        assert isinstance(v, Votation)

        prev_value = getattr(v,key)
        if prev_value != value:
            logger.warning("Update %s to %s (was: %s)" % (key, value, prev_value))
            setattr(v, key, value)
           
              
