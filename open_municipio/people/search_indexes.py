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

    def get_model(self):
        return InstitutionCharge

    def prepare_is_active(self, obj):

        return _("no") if obj.end_date else _("yes")
