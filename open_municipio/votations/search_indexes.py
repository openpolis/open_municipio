from haystack.indexes import *
from haystack import site
from open_municipio.votations.models import Votation


class VotationIndex(SearchIndex):
    text = CharField(document=True, use_template=True)

    # faceting fields
    act_type = FacetCharField( )
    is_key = FacetBooleanField(model_attr='is_key')
    organ = FacetCharField(model_attr='sitting__institution__name')
    votation_date = FacetDateField(model_attr='sitting__date')

    # stored fields, used not to touch DB
    # while showing results
    url = CharField(indexed=False, stored=True)
    title = CharField(indexed=False, stored=True, model_attr='act__title')

    def prepare_act_type(self, obj):
        return obj.act.downcast().__class__.__name__

    def prepare_url(self, obj):
        return obj.get_absolute_url()

    def index_queryset(self):
        """
        Change the default QuerySet to index only linked acts
        """
        return self.model.is_linked_to_act.all()


site.register(Votation, VotationIndex)