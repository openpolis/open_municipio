from django.utils.translation import activate
from haystack import indexes
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
from django.db.models import Q
import logging

from open_municipio.people.models import Institution, InstitutionCharge, Group, GroupCharge, Person, SittingItem, InstitutionResponsability
from open_municipio.acts.models import Act, Agenda,\
    CGDeliberation, Deliberation, Interpellation,\
    Interrogation, Motion, Amendment, Transition,\
    Decision, Decree, Audit, Minute, Speech

class InstitutionChargeIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)

    first_name = indexes.CharField(model_attr='person__first_name')
    last_name = indexes.CharField(model_attr='person__last_name')
    person = indexes.CharField(model_attr='person__slug')
    institution = indexes.FacetCharField()
    group = indexes.MultiValueField(indexed=True, stored=False)
    current_group = indexes.CharField(indexed=True, stored=False)
    responsability = indexes.FacetCharField()
    level = indexes.IntegerField()

    start_date = indexes.FacetDateField(model_attr='start_date')
    end_date = indexes.FacetDateField(model_attr='end_date')

    is_active = indexes.FacetCharField()

    n_presented_acts = indexes.IntegerField(indexed=True, stored=True, model_attr='n_presented_acts')
    n_received_acts = indexes.IntegerField(indexed=True, stored=True, model_attr='n_received_acts')

    n_presented_acts_index = indexes.FloatField()
    n_received_acts_index = indexes.FloatField()

    n_rebel_votations = indexes.IntegerField(indexed=False, stored=True, model_attr='n_rebel_votations')
    n_present_votations = indexes.IntegerField(indexed=False, stored=True, model_attr='n_present_votations')
    n_absent_votations = indexes.IntegerField(indexed=False, stored=True, model_attr='n_absent_votations')
    n_present_attendances = indexes.IntegerField(indexed=False, stored=True, model_attr='n_present_attendances')
    n_absent_attendances = indexes.IntegerField(indexed=False, stored=True, model_attr='n_absent_attendances')
    n_presents = indexes.IntegerField()

    n_present_votations_percent = indexes.FloatField()
    n_present_attendances_percent = indexes.FloatField()
    n_presents_percent = indexes.FloatField()

    n_deliberations = indexes.IntegerField()
    n_cgdeliberations = indexes.IntegerField()
    n_agendas = indexes.IntegerField()
    n_motions = indexes.IntegerField()
    n_motions_agendas = indexes.IntegerField()
    n_amendments = indexes.IntegerField()
    n_interrogations = indexes.IntegerField()
    n_interpellations = indexes.IntegerField()
    n_audits = indexes.IntegerField()
    n_inspection_acts = indexes.IntegerField()

    n_deliberations_index = indexes.FloatField()
    n_cgdeliberations_index = indexes.FloatField()
    n_agendas_index = indexes.FloatField()
    n_motions_index = indexes.FloatField()
    n_motions_agendas_index = indexes.FloatField()
    n_amendments_index = indexes.FloatField()
    n_interrogations_index = indexes.FloatField()
    n_interpellations_index = indexes.FloatField()
    n_audits_index = indexes.FloatField()
    n_inspection_index = indexes.FloatField()

    n_speeches = indexes.IntegerField()
    n_speeches_index = indexes.FloatField()
    speeches_minutes = indexes.IntegerField()
    speeches_minutes_index = indexes.FloatField()

    logger = logging.getLogger('import')

    def get_model(self):
        return InstitutionCharge

    def prepare_institution(self, obj):

        return obj.charge_type if obj.institution.institution_type <= Institution.COUNCIL else ''

    def prepare_group(self, obj):

        return [p['group__slug'] for p in
            GroupCharge.objects.select_related().filter(charge__id=obj.id).values('group__slug').distinct()]

    def prepare_current_group(self, obj):

        return obj.current_groupcharge.group.slug if obj.current_groupcharge else ''

    def prepare_responsability(self, obj):

        if obj.responsabilities.count() >= 1:
            return obj.responsabilities[0].get_charge_type_display()

    def prepare_level(self, obj):

        n = 10 * obj.institution.institution_type

        if obj.responsabilities.count() >= 1:
            n += [i[0] for i in list(InstitutionResponsability.CHARGE_TYPES)].index(obj.responsabilities[0].charge_type)
        else:
            n += 9

        return n

    def prepare_is_active(self, obj):

        return _("no") if obj.end_date else _("yes")

    def prepare_n_presented_acts_index(self, obj):
        return (float(obj.n_presented_acts) / obj.duration.days) * 30 if obj.duration.days else None

    def prepare_n_received_acts_index(self, obj):
        return (float(obj.n_received_acts) / obj.duration.days) * 30 if obj.duration.days else None

    def prepare_n_presents(self, obj):
        return (obj.n_present_attendances \
            if obj.institution.institution_type < Institution.COUNCIL \
            else obj.n_present_votations)

    def prepare_n_present_votations_percent(self, obj):
        n_votations = obj.n_present_votations + obj.n_absent_votations
        return (float(obj.n_present_votations) * 100 / n_votations) if n_votations else 0

    def prepare_n_present_attendances_percent(self, obj):
        n_attendances = obj.n_present_attendances + obj.n_absent_attendances
        return (float(obj.n_present_attendances) * 100 / n_attendances) if n_attendances else 0

    def prepare_n_presents_percent(self, obj):
        n_presents = (obj.n_present_attendances + obj.n_absent_attendances) \
            if obj.institution.institution_type < Institution.COUNCIL \
            else (obj.n_present_votations + obj.n_absent_votations)

        return (float(self.prepare_n_presents(obj)) * 100 / n_presents) if n_presents else 0

    def prepare_n_deliberations(self, obj):
        return obj.presented_act_set.filter(deliberation__isnull=False).count()

    def prepare_n_deliberations_index(self, obj):
        return (float(self.prepare_n_deliberations(obj)) / obj.duration.days) * 30 if obj.duration.days else None

    def prepare_n_cgdeliberations(self, obj):
        return obj.presented_act_set.filter(cgdeliberation__isnull=False).count()

    def prepare_n_cgdeliberations_index(self, obj):
        return (float(self.prepare_n_cgdeliberations(obj)) / obj.duration.days) * 30 if obj.duration.days else None

    def prepare_n_agendas(self, obj):
        return obj.presented_act_set.filter(agenda__isnull=False).count()

    def prepare_n_agendas_index(self, obj):
        return (float(self.prepare_n_agendas(obj)) / obj.duration.days) * 30 if obj.duration.days else None

    def prepare_n_motions(self, obj):
        return obj.presented_act_set.filter(motion__isnull=False).count()

    def prepare_n_motions_index(self, obj):
        return (float(self.prepare_n_motions(obj)) / obj.duration.days) * 30 if obj.duration.days else None

    def prepare_n_motions_agendas(self, obj):
        return obj.presented_act_set.filter(Q(motion__isnull=False) | Q(agenda__isnull=False)).count()

    def prepare_n_motions_agendas_index(self, obj):
        return (float(self.prepare_n_motions_agendas(obj)) / obj.duration.days) * 30 if obj.duration.days else None

    def prepare_n_amendments(self, obj):
        return obj.presented_act_set.filter(amendment__isnull=False).count()

    def prepare_n_amendments_index(self, obj):
        return (float(self.prepare_n_amendments(obj)) / obj.duration.days) * 30 if obj.duration.days else None

    def prepare_n_interrogations(self, obj):
        return obj.presented_act_set.filter(interrogation__isnull=False).count()

    def prepare_n_interrogations_index(self, obj):
        return (float(self.prepare_n_interrogations(obj)) / obj.duration.days) * 30 if obj.duration.days else None

    def prepare_n_interpellations(self, obj):
        return obj.presented_act_set.filter(interpellation__isnull=False).count()

    def prepare_n_interpellations_index(self, obj):
        return (float(self.prepare_n_interpellations(obj)) / obj.duration.days) * 30 if obj.duration.days else None

    def prepare_n_audits(self, obj):
        return obj.presented_act_set.filter(audit__isnull=False).count()

    def prepare_n_audits_index(self, obj):
        return (float(self.prepare_n_audits(obj)) / obj.duration.days) * 30 if obj.duration.days else None

    def prepare_n_inspection_acts(self, obj):
        return obj.presented_act_set.filter(Q(interrogation__isnull=False) | Q(interpellation__isnull=False) | Q(audit__isnull=False)).count()

    def prepare_n_inspection_index(self, obj):
        return (float(self.prepare_n_inspection_acts(obj)) / obj.duration.days) * 30 if obj.duration.days else None

    def prepare_n_speeches(self, obj):
        return obj.n_speeches

    def prepare_n_speeches_index(self, obj):
        return (float(self.prepare_n_speeches(obj)) / obj.duration.days) * 30 if obj.duration.days else None

    def prepare_speeches_minutes(self, obj):
        return (obj.speeches_size / 750)

    def prepare_speeches_minutes_index(self, obj):
        return (float(self.prepare_speeches_minutes(obj)) / obj.duration.days) * 30 if obj.duration.days else None


class GroupIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)

    name = indexes.CharField(indexed=True, model_attr='name')
    acronym = indexes.CharField(indexed=True, model_attr='acronym')

    url = indexes.CharField(indexed=False, stored=True)

    is_active = indexes.FacetCharField()

    n_members = indexes.IntegerField()
    aggregate_charge_duration_days = indexes.IntegerField()

    n_presented_acts = indexes.IntegerField()
    n_presented_acts_index = indexes.FloatField()

    n_presented_deliberations = indexes.IntegerField()
    n_presented_deliberations_index = indexes.FloatField()

    n_presented_agendas = indexes.IntegerField()
    n_presented_agendas_index = indexes.FloatField()

    n_presented_motions = indexes.IntegerField()
    n_presented_motions_index = indexes.FloatField()

    n_presented_motions_agendas = indexes.IntegerField()
    n_presented_motions_agendas_index = indexes.FloatField()

    n_presented_amendments = indexes.IntegerField()
    n_presented_amendments_index = indexes.FloatField()

    n_presented_interrogations = indexes.IntegerField()
    n_presented_interrogations_index = indexes.FloatField()

    n_presented_interpellations = indexes.IntegerField()
    n_presented_interpellations_index = indexes.FloatField()

    n_presented_audits = indexes.IntegerField()
    n_presented_audits_index = indexes.FloatField()

    n_presented_inspection_acts = indexes.IntegerField()
    n_presented_inspection_acts_index = indexes.FloatField()

    logger = logging.getLogger('import')

    def get_model(self):
        return Group

    def prepare_url(self, obj):
        return obj.get_absolute_url()

    def prepare_is_active(self, obj):

        return _("yes") if obj.is_current else _("no")

    def prepare_n_members(self, obj):
        return obj.current_size

    def prepare_aggregate_charge_duration_days(self, obj):
        days = 0
        now = datetime.now().date()

        for gc in obj.groupcharge_set.all():
            start_date = gc.start_date
            end_date = gc.end_date if gc.end_date else now

            if not start_date or start_date > end_date:
                self.logger.warning("invalid start date")
                continue

            days += (end_date - start_date).days

        return days

    def prepare_n_presented_acts_generic(self, obj, act_types=[]):

        now = datetime.now().date()
        query_act_types = Q()
        query_act_support = Q()

        for act_type in act_types:
            query_act_types |= Q(**{ act_type.__name__.lower() + '__isnull' : False })

        for gc in obj.groupcharge_set.all():
            start_date = gc.start_date
            end_date = gc.end_date if gc.end_date else now
            query_act_support |= (Q(actsupport__charge=gc.charge) &
                Q(presentation_date__gte=start_date) &
                Q(presentation_date__lte=end_date))

        return Act.objects.filter(query_act_types & query_act_support).distinct().count()

    def prepare_n_presented_acts(self, obj):
        return self.prepare_n_presented_acts_generic(obj)

    def prepare_n_presented_acts_index(self, obj):
        days = self.prepare_aggregate_charge_duration_days(obj)
        return (float(self.prepare_n_presented_acts(obj)) / days) * 30 if days else None

    def prepare_n_presented_deliberations(self, obj):
        return self.prepare_n_presented_acts_generic(obj, [Deliberation, ])

    def prepare_n_presented_deliberations_index(self, obj):
        days = self.prepare_aggregate_charge_duration_days(obj)
        return (float(self.prepare_n_presented_deliberations(obj)) / days) * 30 if days else None

    def prepare_n_presented_agendas(self, obj):
        return self.prepare_n_presented_acts_generic(obj, [Agenda, ])

    def prepare_n_presented_agendas_index(self, obj):
        days = self.prepare_aggregate_charge_duration_days(obj)
        return (float(self.prepare_n_presented_agendas(obj)) / days) * 30 if days else None

    def prepare_n_presented_motions(self, obj):
        return self.prepare_n_presented_acts_generic(obj, [Motion, ])

    def prepare_n_presented_motions_index(self, obj):
        days = self.prepare_aggregate_charge_duration_days(obj)
        return (float(self.prepare_n_presented_motions(obj)) / days) * 30 if days else None

    def prepare_n_presented_motions_agendas(self, obj):
        return self.prepare_n_presented_acts_generic(obj, [Agenda, Motion])

    def prepare_n_presented_motions_agendas_index(self, obj):
        days = self.prepare_aggregate_charge_duration_days(obj)
        return (float(self.prepare_n_presented_motions_agendas(obj)) / days) * 30 if days else None

    def prepare_n_presented_amendments(self, obj):
        return self.prepare_n_presented_acts_generic(obj, [Amendment, ])

    def prepare_n_presented_amendments_index(self, obj):
        days = self.prepare_aggregate_charge_duration_days(obj)
        return (float(self.prepare_n_presented_amendments(obj)) / days) * 30 if days else None

    def prepare_n_presented_interrogations(self, obj):
        return self.prepare_n_presented_acts_generic(obj, [Interrogation, ])

    def prepare_n_presented_interrogations_index(self, obj):
        days = self.prepare_aggregate_charge_duration_days(obj)
        return (float(self.prepare_n_presented_interrogations(obj)) / days) * 30 if days else None

    def prepare_n_presented_interpellations(self, obj):
        return self.prepare_n_presented_acts_generic(obj, [Interpellation, ])

    def prepare_n_presented_interpellations_index(self, obj):
        days = self.prepare_aggregate_charge_duration_days(obj)
        return (float(self.prepare_n_presented_interpellations(obj)) / days) * 30 if days else None

    def prepare_n_presented_audits(self, obj):
        return self.prepare_n_presented_acts_generic(obj, [Audit, ])

    def prepare_n_presented_audits_index(self, obj):
        days = self.prepare_aggregate_charge_duration_days(obj)
        return (float(self.prepare_n_presented_audits(obj)) / days) * 30 if days else None

    def prepare_n_presented_inspection_acts(self, obj):
        return self.prepare_n_presented_acts_generic(obj, [Interrogation, Interpellation, Audit])

    def prepare_n_presented_inspection_acts_index(self, obj):
        days = self.prepare_aggregate_charge_duration_days(obj)
        return (float(self.prepare_n_presented_inspection_acts(obj)) / days) * 30 if days else None
