from django.utils.translation import activate
from haystack import indexes
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from open_municipio.people.models import Institution, InstitutionCharge, Person, SittingItem

class InstitutionChargeIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)

    person_name = indexes.CharField(model_attr='person__full_name')
    institution = indexes.FacetCharField(model_attr='institution__lowername')

    start_date = indexes.FacetDateField(model_attr='start_date')
    end_date = indexes.FacetDateField(model_attr='end_date')

    is_active = indexes.FacetCharField()

    n_presented_acts = indexes.IntegerField(indexed=False, stored=True, model_attr='n_presented_acts')
    n_received_acts = indexes.IntegerField(indexed=False, stored=True, model_attr='n_received_acts')

    n_rebel_votations = indexes.IntegerField(indexed=False, stored=True, model_attr='n_rebel_votations')
    n_present_votations = indexes.IntegerField(indexed=False, stored=True, model_attr='n_present_votations')
    n_absent_votations = indexes.IntegerField(indexed=False, stored=True, model_attr='n_absent_votations')
    n_present_attendances = indexes.IntegerField(indexed=False, stored=True, model_attr='n_present_attendances')
    n_absent_attendances = indexes.IntegerField(indexed=False, stored=True, model_attr='n_absent_attendances')

    n_deliberations = indexes.IntegerField()
    n_cgdeliberations = indexes.IntegerField()
    n_agendas = indexes.IntegerField()
    n_motions = indexes.IntegerField()
    n_amendments = indexes.IntegerField()
    n_interrogations = indexes.IntegerField()
    n_interpellations = indexes.IntegerField()

    n_deliberations_index = indexes.DecimalField()
    n_cgdeliberations_index = indexes.DecimalField()
    n_agendas_index = indexes.DecimalField()
    n_motions_index = indexes.DecimalField()
    n_amendments_index = indexes.DecimalField()
    n_interrogations_index = indexes.DecimalField()
    n_interpellations_index = indexes.DecimalField()

    def get_model(self):
        return InstitutionCharge

    def prepare_is_active(self, obj):

        return _("no") if obj.end_date else _("yes")

    def prepare_n_deliberations(self, obj):
        return obj.presented_act_set.filter(deliberation__isnull=False).count()

    def prepare_n_cgdeliberations(self, obj):
        return obj.presented_act_set.filter(cgdeliberation__isnull=False).count()

    def prepare_n_agendas(self, obj):
        return obj.presented_act_set.filter(agenda__isnull=False).count()

    def prepare_n_motions(self, obj):
        return obj.presented_act_set.filter(motion__isnull=False).count()

    def prepare_n_amendments(self, obj):
        return obj.presented_act_set.filter(amendment__isnull=False).count()

    def prepare_n_interrogations(self, obj):
        return obj.presented_act_set.filter(interrogation__isnull=False).count()

    def prepare_n_interpellations(self, obj):
        return obj.presented_act_set.filter(interpellation__isnull=False).count()

    def prepare_n_deliberations_index(self, obj):
        return (float(obj.presented_act_set.filter(deliberation__isnull=False).count()) / obj.duration.days) * 30 if obj.duration.days else None

    def prepare_n_cgdeliberations_index(self, obj):
        return (float(obj.presented_act_set.filter(cgdeliberation__isnull=False).count()) / obj.duration.days) * 30 if obj.duration.days else None

    def prepare_n_agendas_index(self, obj):
        return (float(obj.presented_act_set.filter(agenda__isnull=False).count()) / obj.duration.days) * 30 if obj.duration.days else None

    def prepare_n_motions_index(self, obj):
        return (float(obj.presented_act_set.filter(motion__isnull=False).count()) / obj.duration.days) * 30 if obj.duration.days else None

    def prepare_n_amendments_index(self, obj):
        return (float(obj.presented_act_set.filter(amendment__isnull=False).count()) / obj.duration.days) * 30 if obj.duration.days else None

    def prepare_n_interrogations_index(self, obj):
        return (float(obj.presented_act_set.filter(interrogation__isnull=False).count()) / obj.duration.days) * 30 if obj.duration.days else None

    def prepare_n_interpellations_index(self, obj):
        return (float(obj.presented_act_set.filter(interpellation__isnull=False).count()) / obj.duration.days) * 30 if obj.duration.days else None
