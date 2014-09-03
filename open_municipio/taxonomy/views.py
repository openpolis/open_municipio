# -*- coding: utf-8 -*-

from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q
from django.views.generic import DetailView, ListView
from open_municipio.acts.models import Act, Deliberation, Interpellation, Interrogation, Agenda, Motion, Amendment, CGDeliberation
from open_municipio.locations.models import Location
from open_municipio.monitoring.models import Monitoring

from open_municipio.taxonomy.models import Tag, Category, TaggedAct


class TopicListView(ListView):
    model = Category
    template_name = 'taxonomy/topic_list.html'

    def get_context_data(self, **kwargs):
        # call the base implementation first to get a context
        context = super(TopicListView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        context['locations'] = Location.objects.all()

        context['tags_to_cloud'] = list(context['categories']) + list(context['tags']) + list(context['locations'])

        import random
        random.shuffle(context['tags_to_cloud'], lambda : 0.5)

        # collect content type ids
        type_id_list = []
        if context['categories']:
            type_id_list.append(context['categories'][0].content_type_id)
        if context['tags']:
            type_id_list.append(context['tags'][0].content_type_id)
        if context['locations']:
            type_id_list.append(context['locations'][0].content_type_id)

        if type_id_list:
            # create rank of monitorized items
            context['top_monitorized_tags'] = [
                ContentType.objects.get_for_id(m['content_type'])
                    .get_object_for_this_type(pk=m['object_pk'])
                for m in Monitoring.objects
                    .filter(content_type__in=type_id_list)
                    .values('object_pk', 'content_type')
                    .annotate(n_monitoring=Count('object_pk'))
                    .order_by('-n_monitoring')[:10]
            ]
        return context
    
    
class TopicDetailView(DetailView):
    """
    Abstract base class for displaying detail pages of topics (tags + categories).
    """
    context_object_name = 'topic'
    template_name = 'taxonomy/topic_detail.html'
    
    def get_context_data(self, **kwargs):
        # call the base implementation first to get a context
        context = super(TopicDetailView, self).get_context_data(**kwargs)

        context['topics'] = Category.objects.all()
        context['subtopics'] = self.take_subtopics()

        topic = context['topic']
        context['topic_type'] = self.topic_type

        if self.topic_type == 'location':
            tagged_act_id_field = 'act_id'
        else:
            tagged_act_id_field = 'content_object_id'

        ta_ids = set([ta[tagged_act_id_field] for ta in topic.tagged_acts.values(tagged_act_id_field)])

        context['n_acts'] = Act.objects.filter(pk__in=ta_ids).count()

        context['n_deliberation_nonfinal'] = Deliberation.objects.filter(pk__in=ta_ids).filter(~ Q(status__in=(s[0] for s in Deliberation.FINAL_STATUSES))).count()
        context['n_deliberations'] = Deliberation.objects.filter(pk__in=ta_ids).count()
        context['n_cgdeliberation_nonfinal'] = CGDeliberation.objects.filter(pk__in=ta_ids).filter(~ Q(status__in=(s[0] for s in CGDeliberation.FINAL_STATUSES))).count()
        context['n_cgdeliberations'] = CGDeliberation.objects.filter(pk__in=ta_ids).count()
        context['n_motions_nonfinal'] = Motion.objects.filter(pk__in=ta_ids).filter(~ Q(status__in=(s[0] for s in Motion.FINAL_STATUSES))).count()
        context['n_motions'] = Motion.objects.filter(pk__in=ta_ids).count()
        context['n_agendas_nonfinal'] = Agenda.objects.filter(pk__in=ta_ids).filter(~ Q(status__in=(s[0] for s in Agenda.FINAL_STATUSES))).count()
        context['n_agendas'] = Agenda.objects.filter(pk__in=ta_ids).count()
        context['n_interrogations_nonfinal'] = Interrogation.objects.filter(pk__in=ta_ids).filter(~ Q(status__in=(s[0] for s in Interrogation.FINAL_STATUSES))).count()
        context['n_interrogations'] = Interrogation.objects.filter(pk__in=ta_ids).count()
        context['n_interpellations_nonfinal'] = Interpellation.objects.filter(pk__in=ta_ids).filter(~ Q(status__in=(s[0] for s in Interpellation.FINAL_STATUSES))).count()
        context['n_interpellations'] = Interpellation.objects.filter(pk__in=ta_ids).count()
        context['n_amendments_nonfinal'] = Amendment.objects.filter(pk__in=ta_ids).filter(~ Q(status__in=(s[0] for s in Amendment.FINAL_STATUSES))).count()
        context['n_amendments'] = Amendment.objects.filter(pk__in=ta_ids).count()

        return context

    def take_subtopics(self):
        return []
    
class TagDetailView(TopicDetailView):
    model = Tag
    topic_type = 'tag'

    def take_subtopics(self):
        return set([x.category for x in TaggedAct.objects.filter( tag=self.object )])
  
    
class CategoryDetailView(TopicDetailView):
    model = Category
    topic_type = 'category'

    def take_subtopics(self):
        return set([x.tag for x in TaggedAct.objects.filter( category=self.object ) if x.tag])
