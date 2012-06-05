from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.views.generic import DetailView
from django.views.generic.list import ListView
from open_municipio.acts.models import Deliberation, Motion, Interpellation, Emendation, Agenda, Interrogation
from open_municipio.locations.models import Location
from open_municipio.monitoring.models import Monitoring
from open_municipio.people.models import Person, GroupCharge
from open_municipio.taxonomy.models import Category, Tag
from open_municipio.users.models import UserProfile

class UserDetailView(DetailView):

    def get_object(self, queryset=None):

        # object lookup using username
        object = User.objects.get(username=self.kwargs['username'])

        # Return the object
        return object

class UserProfileDetailView(DetailView):
    model = UserProfile
    template_name = 'profiles/profile_detail.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):

        # object lookup using username
        object = UserProfile.objects.get(user__username=self.kwargs['username'])

        # Return the object
        return object

    def get_context_data(self, **kwargs):
        # call the base implementation first to get a context
        context = super(UserProfileDetailView, self).get_context_data(**kwargs)

        context['act_monitoring_list'] = calculate_top_monitorings(
            Deliberation, Motion, Interpellation, Emendation, Agenda, Interrogation,
            user= self.object.user
        )

        context['politician_monitoring_list'] = [el.content_object for el in calculate_top_monitorings(Person, qnt=None, user=self.object.user)]

        context['topic_monitoring_list'] = [el.content_object for el in calculate_top_monitorings(Tag,Category,Location, qnt=None, user=self.object.user)]

        return context


class UserProfileListView(ListView):
    model = UserProfile
    template_name = 'profiles/profile_list.html'

    def get_context_data(self, **kwargs):
        # call the base implementation first to get a context
        context = super(UserProfileListView, self).get_context_data(**kwargs)

        context.update({
            # TODO if a person not have a institution_charge...?
            'top_monitorized_politicians': [p.content_object.all_institution_charges[0] for p in calculate_top_monitorings(Person,qnt=3)],
            'top_monitorized_topics': [el.content_object for el in calculate_top_monitorings(Tag,Category,Location)],
            'top_monitorized_acts': [el.content_object for el in calculate_top_monitorings(Deliberation, Motion, Interpellation, Emendation, Agenda, Interrogation)],
        })
        return context



def calculate_top_monitorings(*models, **kwargs):
    query = dict(content_type__in=[ContentType.objects.get_for_model(m).pk for m in models]) if len(models) > 1 else dict(content_type=ContentType.objects.get_for_model(models[0]).pk)
    if kwargs.get('user'):
       query['user'] = kwargs.get('user')
    return [
        el for el in Monitoring.objects
                 .filter(**query).select_related()
                 .annotate(n_monitoring=Count('object_pk'))
                 .order_by('-n_monitoring')[:kwargs.get('qnt',5)]
    ]
