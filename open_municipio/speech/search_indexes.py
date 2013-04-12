from haystack import indexes
from open_municipio.speech.models import Speech
from django.utils.translation import ugettext_lazy as _

class SpeechIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)   
    date = indexes.DateField(model_attr='date')
    title = indexes.CharField(model_attr='title')

    url = indexes.CharField(indexed=False, stored=True)
    person = indexes.CharField(indexed=True, stored=False)
    act_title = indexes.CharField(indexed=True, stored=True)

    def get_model(self):
        return Speech

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

    def prepare_url(self, obj):
        return obj.get_absolute_url()

    def prepare_person(self, obj):
        return obj.speaker.slug

    def prepare_act_title(self, obj):
        print "prepared %s" % obj.act.title
        return obj.act.title
