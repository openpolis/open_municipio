from haystack import indexes
from open_municipio.acts.models import Act, Speech
from django.utils.translation import activate
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class ActIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    # faceting fields
    act_type = indexes.FacetCharField( )
    is_key = indexes.FacetCharField(model_attr='is_key_yesno')
    initiative = indexes.FacetCharField()
    is_proposal = indexes.FacetCharField()
    organ = indexes.FacetCharField(model_attr='emitting_institution__lowername')
    pub_date = indexes.FacetDateField(model_attr='presentation_date')
    person = indexes.MultiValueField(indexed=True, stored=False)
    tags_with_urls = indexes.MultiValueField(indexed=True, stored=True)
    categories_with_urls = indexes.MultiValueField(indexed=True, stored=True)
    locations_with_urls = indexes.MultiValueField(indexed=True, stored=True)

    # stored fields, used not to touch DB
    # while showing results
    url = indexes.CharField(indexed=False, stored=True)
    title = indexes.CharField(indexed=False, stored=True, model_attr='title')

    def get_model(self):
        return Act

    def prepare_tags_with_urls(self, obj):
        d_obj = obj.downcast()
        return ["%s|%s" % (t.name, t.get_absolute_url()) for t in list(d_obj.tags)] if d_obj else None

    def prepare_categories_with_urls(self, obj):
        d_obj = obj.downcast()
        return ["%s|%s" % (t.name, t.get_absolute_url()) for t in list(d_obj.categories)] if d_obj else None

    def prepare_locations_with_urls(self, obj):
        d_obj = obj.downcast()
        return ["%s|%s" % (t.name, t.get_absolute_url()) for t in list(d_obj.locations)] if d_obj else None
    
    def prepare_act_type(self, obj):
        activate(settings.LANGUAGE_CODE)
        return obj.get_type_name() if obj else None

    def prepare_initiative(self, obj):
        if obj.get_type_name() == 'delibera':
            return obj.downcast().get_initiative_display().lower() if obj.downcast() else None
        else:
            return ''

    def prepare_is_proposal(self, obj):
        if obj.get_type_name() == 'delibera':
            if obj.downcast().final_idnum == '':
                return _('yes')
            else:
                return _('no')

        else:
            return ''

    def prepare_person(self, obj):
        return set(
            [p['person__slug'] for p in
                list(obj.first_signers.values('person__slug').distinct()) +
                list(obj.co_signers.values('person__slug').distinct())]
        )


    def prepare_url(self, obj):
        return obj.downcast().get_absolute_url() if obj.downcast() else None


class SpeechIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)   
    title = indexes.CharField(model_attr='title')

    url = indexes.CharField(indexed=False, stored=True)
    date = indexes.DateField(indexed=True, stored=False)
    person = indexes.CharField(indexed=True, stored=False)

    def get_model(self):
        return Speech

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

    def prepare_url(self, obj):
        return obj.get_absolute_url()

    def prepare_person(self, obj):
        author = obj.author_name_when_external

        if obj.author != None:
            author = obj.author.slug
        
        print "author = %s" % (author, )

        return author

    def prepare_date(self, obj):
        return obj.date
