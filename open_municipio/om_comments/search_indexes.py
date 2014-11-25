from django.utils.translation import activate
from haystack import indexes
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from open_municipio.om_comments.models import CommentWithMood

class CommentWithMoodIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    # faceting fields
    date = indexes.FacetDateField(indexed=True, stored=False)

    # needed to filter votations by person
    #user = indexes.MultiValueField(indexed=True, stored=False)
    month = indexes.FacetCharField()

    def get_model(self):
        return CommentWithMood

    def prepare_date(self, obj):
        return obj.submit_date.date()

    def prepare_month(self, obj):
        return obj.submit_date.strftime("%B")
