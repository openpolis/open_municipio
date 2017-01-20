from django.utils.translation import activate
from haystack import indexes
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from open_municipio.events.models import Event, EventAct
from open_municipio.acts.models import Act

class EventIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    # faceting fields
    date = indexes.FacetDateField(model_attr='date')
    institution = indexes.FacetCharField(model_attr='institution')

    title = indexes.CharField(indexed=False, stored=True, model_attr='title', default='')
    address = indexes.CharField(indexed=False, stored=True, model_attr='address')

    url = indexes.CharField(indexed=False, stored=True)
    n_acts = indexes.IntegerField()

    def get_model(self):
        return Event

    def prepare_url(self, obj):
        return obj.get_absolute_url()

    def prepare_n_acts(self, obj):
        return obj.eventact_set.count()
