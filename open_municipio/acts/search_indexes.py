from haystack import indexes
from open_municipio.acts.models import Act
from django.utils.translation import activate
from django.conf import settings

class ActIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    # faceting fields
    act_type = indexes.FacetCharField( )
    is_key = indexes.FacetCharField(model_attr='is_key_yesno')
    initiative = indexes.FacetCharField()
    organ = indexes.FacetCharField(model_attr='emitting_institution__lowername')
    pub_date = indexes.FacetDateField(model_attr='presentation_date')
    facet_categories = indexes.MultiValueField(indexed=True, stored=True, faceted=True)
    tags_with_urls = indexes.MultiValueField(indexed=False, stored=True)
    categories_with_urls = indexes.MultiValueField(indexed=False, stored=True)
    locations_with_urls = indexes.MultiValueField(indexed=False, stored=True)
    person = indexes.MultiValueField(indexed=True, stored=False)

    # stored fields, used not to touch DB
    # while showing results
    url = indexes.CharField(indexed=False, stored=True)
    title = indexes.CharField(indexed=False, stored=True, model_attr='title')

    def get_model(self):
        return Act

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
        activate(settings.LANGUAGE_CODE)
        return obj.get_type_name()

    def prepare_initiative(self, obj):
        if obj.get_type_name() == 'delibera':
            return obj.downcast().get_initiative_display().lower()
        else:
            return ''

    def prepare_person(self, obj):
        return set(
            [p['person__slug'] for p in obj.first_signers.values('person__slug').distinct()] +
            [p['person__slug'] for p in obj.co_signers.values('person__slug').distinct()]
        )


    def prepare_url(self, obj):
        return obj.downcast().get_absolute_url()

