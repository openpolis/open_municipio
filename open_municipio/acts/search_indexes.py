import datetime
from haystack.indexes import *
from haystack import site
from open_municipio.acts.models import Act


class ActIndex(RealTimeSearchIndex):
    text = CharField(document=True, use_template=True)

    # faceting fields
    act_type = FacetCharField( )
    is_key = FacetBooleanField(model_attr='is_key')
    initiative = FacetCharField()
    organ = FacetCharField(model_attr='emitting_institution__name')
    pub_date = FacetDateField(model_attr='presentation_date')
    facet_categories = MultiValueField(indexed=True, stored=True, faceted=True)
    tags_with_urls = MultiValueField(indexed=False, stored=True)
    categories_with_urls = MultiValueField(indexed=False, stored=True)
    locations_with_urls = MultiValueField(indexed=False, stored=True)

    # stored fields, used not to touch DB
    # while showing results
    url = CharField(indexed=False, stored=True)
    title = CharField(indexed=False, stored=True, model_attr='title')

    def prepare_tags_with_urls(self, obj):
        d_obj = obj.downcast()
        return ["%s|%s" % (t.name, t.get_absolute_url()) for t in list(d_obj.tags)]

    def prepare_categories_with_urls(self, obj):
        d_obj = obj.downcast()
        return ["%s|%s" % (t.name, t.get_absolute_url()) for t in list(d_obj.categories)]

    def prepare_locations_with_urls(self, obj):
        d_obj = obj.downcast()
        return ["%s|%s" % (t.name, t.get_absolute_url()) for t in list(d_obj.locations)]
    
    def prepare_facet_categories(self, obj):
        d_obj = obj.downcast()
        return [c.name for c in list(d_obj.categories) + list(d_obj.tags) + list(d_obj.locations)]

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