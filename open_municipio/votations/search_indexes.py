from django.utils.translation import activate
from haystack import indexes
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from open_municipio.votations.models import Votation, ChargeVote
from open_municipio.acts.models import Transition


class VotationIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    # faceting fields
    act_type = indexes.FacetCharField()
    is_key = indexes.FacetCharField(model_attr='is_key_yesno')
    organ = indexes.FacetCharField(model_attr='sitting__institution__lowername')
    votation_date = indexes.FacetDateField(model_attr='sitting__date')
    n_presents_range = indexes.FacetCharField()
    n_rebels_range = indexes.FacetCharField()
    n_variance = indexes.FacetCharField()

    # stored fields, used not to touch DB
    # while showing results
    url = indexes.CharField(indexed=False, stored=True)
    act_rendered = indexes.CharField(use_template=True, indexed=False)

    act_url = indexes.MultiValueField(indexed=True, stored=True)
    act_descr = indexes.CharField(indexed=False, stored=True, default='')
    title = indexes.CharField(indexed=False, stored=True, model_attr='act__title', default='')
    votation_num = indexes.CharField(indexed=False, stored=True, model_attr='idnum')
    votation_sitting_num = indexes.IntegerField(indexed=False, stored=True, model_attr='sitting__number')
    votation_n_presents = indexes.IntegerField(indexed=True, stored=True, model_attr='n_presents')
    votation_n_yes = indexes.IntegerField(indexed=True, stored=True, model_attr='n_yes')
    votation_n_no = indexes.IntegerField(indexed=True, stored=True, model_attr='n_no')
    votation_n_abst = indexes.IntegerField(indexed=True, stored=True, model_attr='n_abst')
    votation_n_maj = indexes.IntegerField(indexed=True, stored=True, model_attr='n_maj')
    votation_n_rebels = indexes.IntegerField(indexed=True, stored=True, model_attr='n_rebels')
    votation_outcome = indexes.IntegerField(indexed=False, stored=True, model_attr='outcome')
    votation_outcome_display = indexes.FacetCharField(stored=True, default='')
    is_secret = indexes.FacetCharField(stored=True, default='')
    month = indexes.FacetCharField()

    # needed to filter votations by person or charge
    person = indexes.MultiValueField(indexed=True, stored=False)
    charge = indexes.MultiValueField(indexed=True, stored=False)
    charge_present = indexes.MultiValueField(indexed=True, stored=False)
    charge_absent = indexes.MultiValueField(indexed=True, stored=False)
    charge_rebel = indexes.MultiValueField(indexed=True, stored=False)

    def get_model(self):
        return Votation

    def prepare_url(self, obj):
        return obj.get_absolute_url()

    def prepare_act_type(self, obj):
        activate(settings.LANGUAGE_CODE)

        res = _('none')

        related_act = obj.act

        if not related_act:
            transitions = Transition.objects.filter(votation=obj)
            if len(transitions) > 0:
                related_act = transitions[0].act

        if related_act:
            res = related_act.get_type_name()

        return res


    def prepare_act_descr(self, obj):

        res = obj.act_descr

        related_act = obj.act

        if not related_act:
            transitions = Transition.objects.filter(votation=obj)

            if len(transitions) > 0:
                related_act = transitions[0].act

        if related_act:
            res = related_act.adj_title or related_act.title

        return res
        

    def prepare_act_url(self, obj):

        res = set([])

        related_act = obj.act

        if not related_act:

            transitions = Transition.objects.filter(votation=obj)
            if len(transitions) > 0:
                related_act = transitions[0].act

        if related_act:
            res = set([ related_act.downcast().get_absolute_url() ])

        return res


    def prepare_month(self, obj):
        return obj.sitting.date.strftime("%B")

    def prepare_votation_outcome_display(self, obj):
        return obj.get_outcome_display()

    def prepare_person(self, obj):
        return set(
            [p['person__slug'] for p in obj.charge_set.values('person__slug').distinct()]
        )

    def prepare_charge(self, obj):
        return set(
            [p['id'] for p in obj.charge_set.values('id').distinct()]
        ) | \
        set(
            [p['original_charge__id'] for p in obj.charge_set.values('original_charge__id').distinct()]
        )

    def prepare_charge_present(self, obj):
        s = set()
        
        for cv in obj.chargevote_set.filter(
            vote__in=[ChargeVote.VOTES.yes,
                      ChargeVote.VOTES.no,
                      ChargeVote.VOTES.abstained,
                      ChargeVote.VOTES.pres,
                      ChargeVote.VOTES.secret]):

            s.add(cv.charge.id)
            if cv.charge.original_charge: s.add(cv.charge.original_charge.id)
        
        return s

    def prepare_charge_absent(self, obj):
        s = set()
        
        for cv in obj.chargevote_set.filter(vote=ChargeVote.VOTES.absent):
            s.add(cv.charge.id)
            if cv.charge.original_charge: s.add(cv.charge.original_charge.id)
        
        return s

    def prepare_charge_rebel(self, obj):
        #return set(
        #    [cv['charge__id'] for cv in obj.chargevote_set.filter(is_rebel=True).values('charge__id').distinct()]
        #)
        s = set()
        for cv in obj.chargevote_set.filter(is_rebel=True):
            s.add(cv.charge.id)
        return s
 
    def prepare_n_presents_range(self, obj):

        if obj.n_presents <= 12: return '12-'
        elif 13 <= obj.n_presents <= 15: return '13 - 15'
        elif 16 <= obj.n_presents <= 17: return '16 - 17'
        elif 18 <= obj.n_presents <= 22: return '18 - 22'
        else: return '23+'

    def prepare_n_rebels_range(self, obj):

        return str(obj.n_rebels)

    def prepare_n_variance(self, obj):

        v = abs(obj.n_yes - obj.n_no)

        if v <= 2: return '1 - 2'
        elif 3 <= v <= 6: return '3 - 6'
        elif 7 <= v <= 15: return '7 - 15'
        elif 16 <= v <= 22: return '16 - 22'
        else: return '23+'

    def prepare_is_secret(self, obj):

        if obj.is_secret:
            return _('yes')
        else:
            return _('no')
        

    def prepare_properties(self, obj):

        count = obj.majority_vs_minority

        may_presents = count['majority'].get('YES', 0) + count['majority'].get('NO', 0) + \
            count['majority'].get('ABSTAINED', 0) + count['majority'].get('PRES', 0) + \
            count['majority'].get('SECRET', 0)

        min_presents = count['minority'].get('YES', 0) + count['minority'].get('NO', 0) + \
            count['minority'].get('ABSTAINED', 0) + count['minority'].get('PRES', 0) + \
            count['minority'].get('SECRET', 0)

        total_presents = may_presents + min_presents

        may_partecipants = count['majority'].get('YES', 0) + count['majority'].get('NO', 0)
        min_partecipants = count['minority'].get('YES', 0) + count['minority'].get('NO', 0)
        total_partecipants = may_partecipants + min_partecipants

        quorum = (total_partecipants / 2) + 1

        total_yes = count['majority'].get('YES', 0) + count['minority'].get('YES', 0)
        total_no = count['majority'].get('NO', 0) + count['minority'].get('NO', 0)
        total_abst = count['majority'].get('ABSTAINED', 0) + count['minority'].get('ABSTAINED', 0)
        total_pres = count['majority'].get('PRES', 0) + count['minority'].get('PRES', 0)

        if obj.outcome == 1:
            outcome = 'YES'
        elif obj.outcome == 2:
            outcome = 'NO'

        properties = []

        # no numero legale
        if (may_presents < 16):
            properties.append(_("minority decisive for legal number"))

        if ('SECRET' not in count['majority']):

            # si e no si equivalgono: outcome NO
            if total_yes == total_no: quorum = total_yes;

            # minoranza decisiva
            if (count['majority'][outcome] < quorum):
                properties.append(_("minority decisive for outcome"))

        return set(properties)
