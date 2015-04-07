import locale
from haystack import indexes
from open_municipio.acts.models import Act, Speech
from open_municipio.people.models import Institution
from django.utils.translation import activate
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
import logging

locale.setlocale(locale.LC_ALL, 'it_IT.utf8')

class ActIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    # faceting fields
    act_type = indexes.FacetCharField( )
    is_key = indexes.FacetCharField(model_attr='is_key_yesno')
    initiative = indexes.FacetCharField()
    is_proposal = indexes.FacetCharField()
    organ = indexes.FacetCharField(model_attr='emitting_institution__lowername')
    pub_date = indexes.FacetDateField()
    final_date = indexes.DateField()
    person = indexes.MultiValueField(indexed=True, stored=False)
    recipient = indexes.MultiValueField(indexed=True, stored=False)
    tags_with_urls = indexes.MultiValueField(indexed=True, stored=True)
    categories_with_urls = indexes.MultiValueField(indexed=True, stored=True)
    locations_with_urls = indexes.MultiValueField(indexed=True, stored=True)
    has_locations = indexes.FacetCharField()
    idnum = indexes.CharField(indexed=True, stored=False, model_attr='idnum')
    month = indexes.FacetCharField()
    status = indexes.FacetCharField()

    # stored fields, used not to touch DB
    # while showing results
    url = indexes.CharField(indexed=False, stored=True)
    title = indexes.CharField(indexed=False, stored=True)

    logger = logging.getLogger('import')

    def get_model(self):
        return Act

    def prepare_tags_with_urls(self, obj):
        d_obj = obj.downcast()
        return ["%s|%s" % (t.name, t.get_absolute_url()) for t in list(d_obj.tags)] if d_obj else None

    def prepare_categories_with_urls(self, obj):
        d_obj = obj.downcast()
        return ["%s|%s" % (t.name, t.get_absolute_url()) for t in list(d_obj.categories)] if d_obj else None

    def prepare_has_locations(self, obj):
        d_obj = obj.downcast()

        value = _("no")
        if d_obj.locations and len(d_obj.locations) > 0:
            value = _("yes")

        return value

    def prepare_locations_with_urls(self, obj):
        d_obj = obj.downcast()
        return ["%s|%s" % (t.name, t.get_absolute_url()) for t in list(d_obj.locations)] if d_obj else None
    
    def prepare_title(self, obj):

        activate(settings.LANGUAGE_CODE)
        d_obj = obj.downcast()

        if d_obj.get_type_name() == u'emendamento':
            r_title = d_obj.act.adj_title if d_obj.act.adj_title else d_obj.act.title
            r_title += ' - '
        else:
            r_title = ''

        r_title += obj.adj_title if obj.adj_title else obj.title
        return r_title
    
    def prepare_act_type(self, obj):
        activate(settings.LANGUAGE_CODE)
        return obj.get_type_name() if obj else None

    def prepare_initiative(self, obj):

        if obj.downcast().presenter_set.filter(actsupport__charge__institution__institution_type=Institution.MAYOR).count():
            return _("Mayor")

        elif obj.downcast().presenter_set.filter(actsupport__charge__institution__institution_type=Institution.CITY_GOVERNMENT).count():
            return _("Town government")

        elif obj.downcast().presenter_set.filter(actsupport__charge__institution__institution_type=Institution.COUNCIL).count():
            return _("Council")

        return ''


    def prepare_is_proposal(self, obj):

        if obj.downcast().is_final_status(obj.downcast().status):
            return _('no')
        else:
            return _('yes')


    def prepare_pub_date(self, obj):
        """
        Return approval_date or presentation_date as pub_date field,
        according to the status of
        """
        transition = obj.get_first_non_final_transitions()

        return transition.transition_date if transition else obj.presentation_date


    def prepare_final_date(self, obj):
        """
        WRITEME
        """
        transition = obj.get_last_final_transitions()

        if (transition):
            return transition.transition_date

        this = obj.downcast()

        return this.approval_date if hasattr(this, 'approval_date') else obj.presentation_date


    def prepare_person(self, obj):
        return [p['person__slug'] for p in
                list(obj.first_signers.values('person__slug').distinct()) +
                list(obj.co_signers.values('person__slug').distinct())]


    def prepare_recipient(self, obj):
        return [p['person__slug'] for p in
                list(obj.recipients.values('person__slug').distinct())]


    def prepare_url(self, obj):
        return obj.downcast().get_absolute_url() if obj.downcast() else None

    def prepare_month(self, obj):
        return obj.presentation_date.strftime("%B")

    def prepare_status(self, obj):
        return obj.downcast().get_status_display()


class SpeechIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)   
    title = indexes.CharField(model_attr='title')

    url = indexes.CharField(indexed=False, stored=True)
    date = indexes.DateField(indexed=True, stored=False)
    person = indexes.MultiValueField(indexed=True, stored=False)

    act_url = indexes.MultiValueField(indexed=True, stored=True)
    month = indexes.FacetCharField()

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
        
        return [ author, ]

    def prepare_date(self, obj):
        return obj.date

    def prepare_month(self, obj):
        return obj.sitting.date.strftime("%B")

    def prepare_act_url(self, obj):
#        return [act.get_short_url() for act in obj.ref_acts]
        res = [act.get_absolute_url() for act in obj.ref_acts]
#        print "prepare act url for speech: %s" % res

        return res


locale.setlocale(locale.LC_ALL, '')
