import locale
from django.utils.html import strip_tags
from HTMLParser import HTMLParser
from haystack import indexes
from open_municipio.acts.models import Act, Speech, ActSupport, Amendment
from open_municipio.people.models import Institution
from open_municipio.votations.models import Votation, ChargeVote
from open_municipio.attendances.models import Attendance, ChargeAttendance
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
    pub_date = indexes.FacetDateField(model_attr='first_date')
    final_date = indexes.DateField(model_attr='final_date')
    person = indexes.MultiValueField(indexed=True, stored=False)
    charge = indexes.MultiValueField(indexed=True, stored=False)
    group = indexes.MultiValueField(indexed=True, stored=False)
    recipient = indexes.MultiValueField(indexed=True, stored=False)
    tag = indexes.MultiValueField(indexed=True, stored=True, faceted=True)
    category = indexes.MultiValueField(indexed=True, stored=True, faceted=True)
    location = indexes.MultiValueField(indexed=True, stored=True, faceted=True)
    has_locations = indexes.FacetCharField()
    idnum = indexes.CharField(indexed=True, stored=False, model_attr='idnum')
    month = indexes.FacetCharField()
    status = indexes.FacetCharField()
    iter_duration = indexes.FacetCharField()
    multiple_supporters = indexes.FacetCharField()

    # stored fields, used not to touch DB
    # while showing results
    url = indexes.CharField(indexed=False, stored=True)
    title = indexes.CharField(indexed=True, stored=True)
    adj_title = indexes.CharField(indexed=True, stored=True)

    charge_supporting = indexes.MultiValueField(indexed=True, stored=False)
    charge_not_supporting = indexes.MultiValueField(indexed=True, stored=False)

    logger = logging.getLogger('import')

    def get_model(self):
        return Act

    def prepare_tag(self, obj):
        d_obj = obj.downcast()
        return [t.name for t in list(d_obj.tags)] if d_obj else None

    def prepare_category(self, obj):
        d_obj = obj.downcast()
        return [t.name for t in list(d_obj.categories)] if d_obj else None

    def prepare_location(self, obj):
        d_obj = obj.downcast()
        return [t.name for t in list(d_obj.locations)] if d_obj else None

    def prepare_has_locations(self, obj):
        d_obj = obj.downcast()

        value = _("no")
        if d_obj.locations and len(d_obj.locations) > 0:
            value = _("yes")

        return value
    
    def prepare_title(self, obj):

        activate(settings.LANGUAGE_CODE)
        return obj.title

    def prepare_adj_title(self, obj):

        r_title = obj.adj_title
        d_obj = obj.downcast()

        if isinstance(d_obj, Amendment):
            if d_obj.act.adj_title:
                if obj.adj_title:
                    r_title = "%s - %s" % (d_obj.act.adj_title, obj.adj_title)
                else:
                    r_title = "%s - %s" % (d_obj.act.adj_title, obj.title)

        return r_title

    
    def prepare_act_type(self, obj):
        activate(settings.LANGUAGE_CODE)
        return obj.get_type_name() if obj else None

    def prepare_initiative(self, obj):

        if obj.downcast().presenter_set.filter(actsupport__charge__institution__institution_type=Institution.COUNCIL).count():
            return _("Council")

        elif obj.downcast().presenter_set.filter(actsupport__charge__institution__institution_type=Institution.CITY_GOVERNMENT).count():
            return _("Town government")

        elif obj.downcast().presenter_set.filter(actsupport__charge__institution__institution_type=Institution.MAYOR).count():
            return _("Mayor")

        return ''


    def prepare_is_proposal(self, obj):

        if obj.downcast().is_final_status(obj.downcast().status):
            return _('no')
        else:
            return _('yes')

    def prepare_person(self, obj):

        return [p['person__slug'] for p in
                list(obj.first_signers.values('person__slug').distinct()) +
                list(obj.co_signers.values('person__slug').distinct())]

    def prepare_charge(self, obj):
        return [str(c.id) for c in list(obj.presenters.distinct())]

    def prepare_group(self, obj):

        group_list = set()
        date_default = obj.first_date

        for supp in ActSupport.objects.filter(act__id=obj.pk):
            d = supp.support_date if supp.support_date else date_default
            g = supp.charge.current_at_moment_groupcharge(d.strftime("%Y-%m-%d"))
            if (g): group_list.add(g.group)

        return [g.slug for g in group_list]

    def prepare_recipient(self, obj):
        return [p['person__slug'] for p in
                list(obj.recipients.values('person__slug').distinct())]


    def prepare_url(self, obj):
        return obj.downcast().get_absolute_url() if obj.downcast() else None

    def prepare_month(self, obj):
        return obj.presentation_date.strftime("%B")

    def prepare_status(self, obj):
        return obj.downcast().get_status_display()

    def prepare_iter_duration(self, obj):

        if not obj.iter_duration.days: return '0'
        elif obj.iter_duration.days <= 7: return '1 - 7'
        elif obj.iter_duration.days <= 14: return '8 - 14'
        elif obj.iter_duration.days <= 21: return '15 - 21'
        elif obj.iter_duration.days <= 30: return '21 - 30'
        elif obj.iter_duration.days <= 60: return 'oltre un mese'
        else: return 'oltre due mesi'

    def prepare_multiple_supporters(self, obj):
        return _("yes") if obj.presenter_set.count() > 1 else _("no")

    def prepare_charge_supporting(self, obj):
        s = set()

        last_transition = obj.downcast().get_last_final_transitions()

        #if not last_transition:
        #    self.logger.warning("no last transition for '%s'" % obj.title)

        if last_transition:

            #if not last_transition.votation and not last_transition.attendance:
            #    self.logger.warning("no votation nor attendance for %s %s '%s'" % (obj.emitting_institution, obj.presentation_date, obj.title))

            # find by votation
            try:
                for cv in last_transition.votation.chargevote_set.filter(
                    vote=ChargeVote.VOTES.yes):
                    s.add(cv.charge.id)
                    if cv.charge.original_charge: s.add(cv.charge.original_charge.id)
            except Exception, e:
                pass

            # find by attendance
            try:
                for ca in last_transition.attendance.chargeattendance_set.filter(
                    value=ChargeAttendance.VALUES.pres):
                    s.add(ca.charge.id)
                    if ca.charge.original_charge: s.add(ca.charge.original_charge.id)
            except Exception, e:
                pass

        return s

    def prepare_charge_not_supporting(self, obj):
        s = set()

        last_transition = obj.downcast().get_last_final_transitions()
        if last_transition:

            # find by votation
            try:
                for cv in last_transition.votation.chargevote_set.exclude(
                    vote=ChargeVote.VOTES.yes):
                    s.add(cv.charge.id)
                    if cv.charge.original_charge: s.add(cv.charge.original_charge.id)
            except Exception, e:
                pass

            # find by attendance
            try:
                for ca in last_transition.attendance.chargeattendance_set.exclude(
                    value=ChargeAttendance.VALUES.pres):
                    s.add(ca.charge.id)
                    if ca.charge.original_charge: s.add(ca.charge.original_charge.id)
            except Exception, e:
                pass

        return s


class SpeechIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)   
    title = indexes.CharField(indexed=True, stored=True)
    seq_order = indexes.IntegerField(model_attr='seq_order')

    url = indexes.CharField(indexed=False, stored=True)
    date = indexes.DateField(indexed=True, stored=False)
    person = indexes.MultiValueField(indexed=True, stored=False)
    charge = indexes.MultiValueField(indexed=True, stored=False)

    act_url = indexes.MultiValueField(indexed=True, stored=True)
    sitting_number = indexes.IntegerField(indexed=False, stored=True)
    sitting_url = indexes.CharField(indexed=False, stored=True)
    sitting_item_url = indexes.CharField(indexed=False, stored=True)
    month = indexes.FacetCharField()

    htmlparser = HTMLParser()

    def prepare_text(self, obj):
        activate(settings.LANGUAGE_CODE)

        plain_text = SpeechIndex.htmlparser.unescape(strip_tags(obj.text))

        return plain_text

    def prepare_title(self, obj):

        activate(settings.LANGUAGE_CODE)

        return obj.title if obj.title else obj.sitting_item.title

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

    def prepare_charge(self, obj):

        if obj.author:
            return [str(c.id) for c in obj.author.get_current_institution_charges(obj.date.strftime("%Y-%m-%d"))]

    def prepare_sitting_number(self, obj):
        return obj.sitting_item.sitting.number

    def prepare_sitting_url(self, obj):
        return obj.sitting_item.sitting.get_absolute_url()

    def prepare_sitting_item_url(self, obj):
        return obj.sitting_item.get_absolute_url()

    def prepare_date(self, obj):
        return obj.date

    def prepare_month(self, obj):
        return obj.sitting.date.strftime("%B")

    def prepare_act_url(self, obj):
#        return [act.get_short_url() for act in obj.ref_acts]
        res = [act.get_absolute_url() for act in obj.ref_acts]

        return res

locale.setlocale(locale.LC_ALL, '')
