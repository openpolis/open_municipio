from django.utils.translation import activate
from haystack import indexes
from django.conf import settings

from open_municipio.votations.models import Votation


class VotationIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    # faceting fields
    act_type = indexes.FacetCharField( )
    is_key = indexes.FacetCharField(model_attr='is_key_yesno')
    organ = indexes.FacetCharField(model_attr='sitting__institution__lowername')
    votation_date = indexes.FacetDateField(model_attr='sitting__date')

    # stored fields, used not to touch DB
    # while showing results
    url = indexes.CharField(indexed=False, stored=True)
    act_url = indexes.CharField(indexed=True, stored=True)
    title = indexes.CharField(indexed=False, stored=True, model_attr='act__title')
    votation_num = indexes.CharField(indexed=False, stored=True, model_attr='idnum')
    votation_sitting_num = indexes.IntegerField(indexed=False, stored=True, model_attr='sitting__number')
    votation_n_presents = indexes.IntegerField(indexed=False, stored=True, model_attr='n_presents')
    votation_n_yes = indexes.IntegerField(indexed=False, stored=True, model_attr='n_yes')
    votation_n_no = indexes.IntegerField(indexed=False, stored=True, model_attr='n_no')
    votation_n_abst = indexes.IntegerField(indexed=False, stored=True, model_attr='n_abst')
    votation_n_maj = indexes.IntegerField(indexed=False, stored=True, model_attr='n_maj')
    votation_n_rebels = indexes.IntegerField(indexed=False, stored=True, model_attr='n_rebels')
    votation_outcome = indexes.CharField(indexed=False, stored=True, model_attr='outcome', default='')

    def get_model(self):
        return Votation

    def prepare_url(self, obj):
        return obj.get_absolute_url()

    def prepare_act_type(self, obj):
        activate(settings.LANGUAGE_CODE)
        return obj.act.get_type_name()

    def prepare_act_url(self, obj):
        return obj.act.downcast().get_absolute_url()

    def index_queryset(self):
        """
        Change the default QuerySet to index only linked acts
        """
        return self.get_model().is_linked_to_act.all()


