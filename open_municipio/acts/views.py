from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponseNotAllowed
from django.utils.decorators import method_decorator
from django.views.generic import View, DetailView, ListView
from django.views.generic.edit import FormView
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.decorators import user_passes_test, login_required

from open_municipio.acts.models import Act, Agenda, Deliberation, Interpellation, Interrogation, Motion, Transition
from open_municipio.acts.forms import ActDescriptionForm, ActTransitionForm, ActFinalTransitionForm, ActTitleForm

from open_municipio.monitoring.forms import MonitoringForm

from open_municipio.om_search.forms import RangeFacetedSearchForm
from open_municipio.om_search.views import ExtendedFacetedSearchView

from open_municipio.taxonomy.models import Tag, Category

from open_municipio.locations.forms import ActLocationsAddForm          

import re

from django.utils import simplejson as json


class ActSearchView(ExtendedFacetedSearchView):
    """

    This view allows faceted search and navigation of the acts.

    It extends an extended version of the basic FacetedSearchView,
    and can be customized whenever

    """
    __name__ = 'ActSearchView'

    def __init__(self, *args, **kwargs):
        # Needed to switch out the default form class.
        if kwargs.get('form_class') is None:
            kwargs['form_class'] = RangeFacetedSearchForm

        super(ActSearchView, self).__init__(*args, **kwargs)

    def build_form(self, form_kwargs=None):
        if form_kwargs is None:
            form_kwargs = {}

        # This way the form can always receive a list containing zero or more
        # facet expressions:
        form_kwargs['selected_facets'] = self.request.GET.getlist("selected_facets")

        return super(ActSearchView, self).build_form(form_kwargs)

    def extra_context(self):
        """
        Add extra content here, when needed
        """
        extra = super(ActSearchView, self).extra_context()
        extra['base_url'] = reverse('om_act_search') + '?' + extra['params'].urlencode()


        return extra



from django.http import HttpResponse

class ActListView(ListView):
    template_name = 'acts/act_list.html'
    queryset = Act.objects.select_subclasses().order_by('-presentation_date')
    context_object_name = 'acts'
    
    def get_context_data(self, **kwargs):
        # call the base implementation first to get a context
        context = super(ActListView, self).get_context_data(**kwargs)
        context['key_acts'] = Act.featured.all()
        
        return context


class ActLiveEditView(FormView):
    def dispatch(self, *args, **kwargs):
        return super(ActLiveEditView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        response_data = {}
        try:
            if not self.request.user.is_authenticated() or not self.kwargs.get('pk') == request.POST.get('id'):
                raise Exception('NOT_ALLOWED1')

            target_act = Act.objects.get(pk=self.kwargs.get('pk'))
            target_act_field = self.request.POST.get('act_field')

            if target_act_field == 'title':
                if not request.user.has_perm('acts.change_act'):
                    raise Exception('NOT_ALLOWED2')
                form = ActTitleForm(self.request.POST, instance=target_act)

            elif target_act_field == 'description':
                if not (self.request.user.get_profile().person and\
                   self.request.user.get_profile().person in [p.person for p in target_act.presenters]):
                    raise Exception('NOT_ALLOWED3')
                form = ActDescriptionForm(self.request.POST, instance=target_act)

            else:
                raise Exception('INVALID_FIELD')

            if not form.is_valid():
                raise Exception( form.errors )

            form.save()
            response_data['text'] = form.cleaned_data[ target_act_field ]

        except Act.DoesNotExist:
            response_data['error'] = 'ACT_NOT_FOUND'
        except Exception as e:
            response_data['error'] = e.args[0]

        return HttpResponse(json.dumps(response_data), mimetype="application/json")


class ActDetailView(DetailView):
    model = Act
    context_object_name = 'act'

    def get_context_data(self, **kwargs):
        # the monitored act
        # it's a deliberation, not an act, from the urls
        act = self.get_object()

        # call the base implementation first to get a context
        context = super(ActDetailView, self).get_context_data(**kwargs)
        # mix-in tab-related context
        self.tab = self.kwargs.get('tab', 'default')
        extra_context = getattr(self, 'get_related_%(tab)s' % {'tab': self.tab})()
        if extra_context:
            context.update(extra_context)

        if self.request.user.has_perm('acts.change_act'):
            # add a form for editing title of act
            context['title_form'] = ActTitleForm(initial = {
                'id': act.pk,
                'title': act.title,
                })
 
        if self.request.user.has_perm('locations.change_taggedactbylocation'):
            # add a form for classifying an act using locations
            context['location_form'] = ActLocationsAddForm(initial = {
                'act': act,
                'locations': act.locations,
                })
        
        # add a form for the description of the act
        signers = [p.person for p in act.presenters]
        try:
            if self.request.user.is_authenticated() and\
               self.request.user.get_profile().person and \
               self.request.user.get_profile().person in signers:
                context['description_form'] = ActDescriptionForm(initial = {
                    'id': act.pk,
                    'description': act.description,
                })
        except ObjectDoesNotExist:
            context['description_form'] = False
        
        # is the user monitoring the act?
        context['is_user_monitoring'] = False
        try:
            if self.request.user.is_authenticated():
                # add a monitoring form, to context,
                # to switch monitoring on and off
                context['monitoring_form'] = MonitoringForm(data = {
                    'content_type_id': act.content_type_id,
                    'object_pk': act.id,
                    'user_id': self.request.user.id
                })
                
                if act in self.request.user.get_profile().monitored_objects:
                    context['is_user_monitoring'] = True
        except ObjectDoesNotExist:
            context['is_user_monitoring'] = False

        # some user can edit categories and tags
        if self.request.user.has_perm('taxonomy.change_taggedact'):
            # all categories and tags
            context['topics'] = {
                'categories' : Category.objects.all(),
                'tags' : Tag.objects.all()
            }

        # retrieve a dictionary with status and its transitions
        context['transition_groups'] = act.get_transitions_groups()

        # some user can set transitions
        if self.request.user.has_perm('acts.change_transition') : #and context['status_list']
            context['transition_forms'] = {}
            if len(context['transition_groups']) == 5:
                context['transition_forms']['transition_to_council_form'] = ActTransitionForm(initial={'act': act, 'final_status': 'COUNCIL' },prefix="council")
                context['transition_forms']['transition_to_committee_form'] = ActTransitionForm(initial={'act': act, 'final_status': 'COMMITTEE' },prefix="committee")
            context['transition_forms']['transition_to_final_form'] = ActFinalTransitionForm(initial={'act': act },prefix="final")
            context['transition_forms']['transition_to_final_form'].fields['final_status'].widget.choices = act.FINAL_STATUSES

        return context
    
    def get_related_default(self):
        """
        Retrieve context needed for populating the default tab.
        """
        pass
    
    def get_related_emendations(self):
        """
        Retrieve context needed for populating the *emendations* tab.
        """
        pass

    def get_related_documents(self):
        """
        Retrieve context needed for populating the *documents* tab.
        """
        pass
    
    def get_template_names(self):
        if self.tab == 'default': # default tab selected
            return 'acts/%(model)s_detail.html' % {'model': self.model.__name__.lower()}
        else:
            return 'acts/%(model)s_detail_%(tab)s.html' % {'model': self.model.__name__.lower(), 'tab': self.tab}


class AgendaDetailView(ActDetailView):
    model = Agenda
    

class DeliberationDetailView(ActDetailView):
    model = Deliberation


class InterpellationDetailView(ActDetailView):
    model = Interpellation


class InterrogationDetailView(ActDetailView):
    model = Interrogation


class MotionDetailView(ActDetailView):
    model = Motion
    

## tags/categories management
class ActTagEditorView(View):
    """
    Server-side component of the "Act-Tag-Editor" widget.
    """
    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super(ActTagEditorView, self).dispatch(*args, **kwargs)
    
    def get_object(self):
        """
        Returns the ``Act`` instance being tagged.
        """
        tagged_act = get_object_or_404(Act, pk=self.kwargs.get('pk'))
        return tagged_act
    
    def get_success_url(self):
        # on success, redirect to act's detail page
        return self.tagged_act.downcast().get_absolute_url()
    
    def post(self, request, *args, **kwargs):
        tagged_act = self.tagged_act = self.get_object()
        new_topics = {} # new set of topics (categories + tags) for the act
        r = re.compile(r'^categories\[(\d+)\]$')
        new_tags_ids = set()
        new_tags = set()
        for param in self.request.POST:
            if r.match(param):
                m = r.match(param)
                category = get_object_or_404(Category, pk=int(m.group(1)))
                new_topics[category] = []
                tag_ids = self.request.POST[param].split(',')
                if tag_ids != [u'']: # if this category has been associated to at least one tag
                    new_tags_ids |= set(tag_ids) 
                    for tag_id in tag_ids:
                        tag = get_object_or_404(Tag, id=int(tag_id))
                        new_topics[category].append(tag)
                        new_tags.add(tag)

        old_tags = set(tagged_act.tags)
        old_categories = set(tagged_act.categories)

        # decrement count of removed tags
        for tag in old_tags - new_tags:
            tag.count -= 1
            if tag.count < 0:
                tag.count = 0
            tag.save()

        # decrement count of removed categories
        for cat in old_categories - set(new_topics.keys()):
            cat.count -= 1
            if cat.count < 0:
                cat.count = 0
            cat.save()

        # remove old topics
        tagged_act.tag_set.clear()

        # adding new topics
        for cat in new_topics.keys():
            tagged_act.tag_set.add(*new_topics.get(cat), tagger=self.request.user, category=cat)
            # increment added categories
            if cat not in old_categories:
                cat.count += 1
                cat.save()

        # increment added tags
        for tag in new_tags - old_tags:
            tag.count += 1
            tag.save()
        
        return HttpResponseRedirect(self.get_success_url())   
 
    
class ActTransitionToggleBaseView(FormView):
    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super(ActTransitionToggleBaseView, self).dispatch(*args, **kwargs)

    def form_invalid(self, form=None):
        msg = "Invalid transition for this act!"
        return HttpResponseBadRequest(msg)

    def get_success_url(self):
        return self.act.downcast().get_absolute_url()

    def get(self, *args, **kwargs):
        return HttpResponseNotAllowed(['POST'])


class ActTransitionAddView(ActTransitionToggleBaseView):
    def post(self, request, *args, **kwargs):
        self.act = get_object_or_404(Act, pk=kwargs['pk'])
        nameprefix = request.POST.get('prefix', '')

        if 'final' == nameprefix:
            form = ActFinalTransitionForm(request.POST,prefix=nameprefix)
            form.fields['final_status'].widget.choices = self.act.downcast().FINAL_STATUSES
        else:
            form = ActTransitionForm(request.POST,prefix=nameprefix)

        if not form.is_valid():
            return self.form_invalid(form)

        form.save()

        return HttpResponseRedirect( self.get_success_url() )


class ActTransitionRemoveView(ActTransitionToggleBaseView):
    def post(self, request, *args, **kwargs):
        """
        TODO: clean transition from news, act's status and status_is_final
        """
        self.act = get_object_or_404(Act, pk=kwargs['pk'])

        transition = get_object_or_404(Transition, pk=request.POST['transition_id'])
        transition.delete()

        return HttpResponseRedirect( self.get_success_url() )
