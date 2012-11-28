from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.views.generic import DetailView
from django.views.generic.list import ListView
from open_municipio.acts.models import Deliberation, Motion, Interpellation, Amendment, Agenda, Interrogation
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
        try:
            object = UserProfile.objects.get(user__username=self.kwargs['username'])

            # Return the object
            return object
        except ObjectDoesNotExist:
            pass

    def get_context_data(self, **kwargs):
        # call the base implementation first to get a context
        context = super(UserProfileDetailView, self).get_context_data(**kwargs)

        if  self.object:
            context['act_monitoring_list'] = calculate_top_monitorings(
                Deliberation, Motion, Interpellation, Amendment, Agenda, Interrogation,
                user = self.object.user
            )

            context['politician_monitoring_list'] = extract_top_monitored_objects(Person, qnt=None, user=self.object.user)

            context['topic_monitoring_list'] = extract_top_monitored_objects(Tag,Category,Location, qnt=None, user=self.object.user)

            social_accounts = []
            user_social_accounts = [ac.provider for ac in self.object.user.social_auth.all()]
            for account in settings.SOCIAL_AUTH_BACKENDS_LIST.keys():
                if account in user_social_accounts:
                    social_accounts.append({'name': account, 'is_connected': True})
                else:
                    social_accounts.append({'name': account, 'is_connected': False})
            context['user_social_accounts'] = [settings.SOCIAL_AUTH_BACKENDS_LIST[a] for a in user_social_accounts]
            context['social_accounts'] = social_accounts


        return context


class UserProfileListView(ListView):
    model = UserProfile
    template_name = 'profiles/profile_list.html'

    def get_context_data(self, **kwargs):
        # call the base implementation first to get a context
        context = super(UserProfileListView, self).get_context_data(**kwargs)

        context.update({
            # TODO if a person not have a institution_charge...?
            'top_monitored_politicians': extract_top_monitored_objects(Person,qnt=3),
            'top_monitored_topics': extract_top_monitored_objects(Tag,Category,Location),
            'top_monitored_acts': extract_top_monitored_objects(Deliberation, Motion, Interpellation, Agenda, Interrogation),
        })
        return context



def extract_top_monitored_objects(*models, **kwargs):
    """
    Given a list of models, returns a list of monitored objects, annotated with the number of monitoring users
    The list is sorted by the number of monitoring users, descending order.

    The last kwargs['qnt'] results are returned, with qnt set to 10 by default
    """

    query = dict(content_type__in=ContentType.objects.get_for_models(*models).values())
    if kwargs.get('user'):
        query['user'] = kwargs.get('user')

    # what TOP means
    limit = kwargs.get('qnt', 10)

    monitored_objects = []
    for el in Monitoring.objects.\
            filter(**query).\
            values('content_type', 'object_pk').distinct().\
            annotate(n_monitoring=Count('object_pk')).\
            order_by('-n_monitoring')[:limit]:
        ct = ContentType.objects.get(pk=el['content_type'])
        object = ct.get_object_for_this_type(pk=el['object_pk'])
        monitored_objects.append({'content_type': ct, 'object': object, 'n_monitoring': el['n_monitoring']})

    return monitored_objects

def calculate_top_monitorings(*models, **kwargs):
    if len(models):
        query = dict(content_type__in=[ContentType.objects.get_for_model(m).pk for m in models])
    else:
        query = dict(content_type=ContentType.objects.get_for_model(models[0]).pk)
    if kwargs.get('user'):
       query['user'] = kwargs.get('user')
    return [
        el for el in Monitoring.objects
                 .filter(**query).select_related()
                 .annotate(n_monitoring=Count('object_pk'))
                 .order_by('-n_monitoring')[:kwargs.get('qnt',10)]
    ]
