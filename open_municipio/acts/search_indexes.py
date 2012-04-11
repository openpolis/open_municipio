import datetime
from haystack.indexes import *
from haystack import site
from open_municipio.acts.models import Act


class ActIndex(SearchIndex):
    text = CharField(document=True, use_template=True)

    # faceting fields
    act_type = FacetCharField( )
    is_key = FacetBooleanField(model_attr='is_key')
    initiative = FacetCharField()
    organ = FacetCharField(model_attr='emitting_institution__name')
    pub_date = FacetDateField(model_attr='presentation_date')
    categories = MultiValueField(indexed=True, stored=True, faceted=True)
    tags = MultiValueField(indexed=True, stored=True, faceted=True)


    # stored fields, used not to touch DB
    # while showing results
    url = CharField(indexed=False, stored=True)
    title = CharField(indexed=False, stored=True, model_attr='title')

    def prepare_categories(self, obj):
        return [c.name for c in obj.categories]

    def prepare_tags(self, obj):
        return [tag.name for tag in obj.tags]

    def prepare_act_type(self, obj):
        return obj.downcast().__class__.__name__

    def prepare_initiative(self, obj):
        if obj.downcast().__class__.__name__ == 'Deliberation':
            return obj.downcast().get_initiative_display()
        else:
            return ''

    def prepare_url(self, obj):
        return obj.downcast().get_absolute_url()


site.register(Act, ActIndex)