from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponseNotAllowed
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import FormView
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse

from django.contrib.auth.decorators import login_required

from open_municipio.acts.models import Act, Agenda, Deliberation, Interpellation, Interrogation, Motion, Transition
from open_municipio.acts.forms import TagAddForm, ActDescriptionForm, ActTransitionForm, ActFinalTransitionForm

from open_municipio.monitoring.forms import MonitoringForm

from open_municipio.om_search.forms import RangeFacetedSearchForm
from open_municipio.om_search.views import ExtendedFacetedSearchView

from open_municipio.taxonomy.models import Tag, Category
from open_municipio.taxonomy.views import AddTagsView, RemoveTagView



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


class ActListView(ListView):
    template_name = 'acts/act_list.html'
    queryset = Act.objects.select_subclasses().order_by('-presentation_date')
    context_object_name = 'acts'
    
    def get_context_data(self, **kwargs):
        # call the base implementation first to get a context
        context = super(ActListView, self).get_context_data(**kwargs)
        context['key_acts'] = Act.featured.all()
        
        return context
    

class ActEditorView(TemplateView):
    pass


class ActDescriptionView(FormView):
    form_class = ActDescriptionForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ActDescriptionView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        instead of saving the form, just extract the act from the ID
        and change its description
        """
        act = Act.objects.select_subclasses().get(pk=form.cleaned_data['id'])
        description = form.cleaned_data['description']
        act.description = description
        act.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form=None):
        msg = "It appears that the act's description form has been tampered with !"
        return HttpResponseBadRequest(msg)

    def get_success_url(self):
        # FIXME: redirects shouldn't rely on the ``Referer`` header,
        # since it might be missing from the HTTP request,
        # depending on client's configuration.
        return self.request.META['HTTP_REFERER']

    def get(self, *args, **kwargs):
        msg = "This view can be accessed only via POST"
        return HttpResponseNotAllowed(msg)


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
            
        # Add in a form for adding tags
        context['tag_add_form'] = TagAddForm()

        # add a form for the description of the act
        signers = [p.person for p in act.presenters]
        try:
            if self.request.user.is_authenticated() and\
               self.request.user.get_profile().person and \
               self.request.user.get_profile().person in signers:
                context['description_form'] = ActDescriptionForm(data = {
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
            context['act_tags_editor'] = {
                'categories' : Category.objects.all(),
                'tags' : Tag.objects.all()
            }

        # retrieve a dictionary with status and its transitions
        context['transition_groups'] = act.get_transitions_groups()

        context['transition_forms'] = {}
        # some user can set transitions
        if self.request.user.has_perm('acts.add_transition') : #and context['status_list']
            if len(context['transition_groups']) == 5:
                context['transition_to_council_form'] = ActTransitionForm(initial={'act': act, 'final_status': 'COUNCIL' })
                context['transition_to_committee_form'] = ActTransitionForm(initial={'act': act, 'final_status': 'COMMITTEE' })
            context['transition_to_final_form'] = ActFinalTransitionForm(initial={'act': act })
            context['transition_to_final_form'].fields['final_status'].widget.choices = [('APPROVED','Approvato'),('REJECTED','Rifiutato')]

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
    

## Tag management
class ActAddTagsView(AddTagsView):
    form_class = TagAddForm
    context_object_name = 'act'
    template_name = 'acts/act_detail.html'
  
    def get_object(self):
        """
        Returns the ``Act`` instance being tagged.
        """
        act = get_object_or_404(Act, pk=self.kwargs['pk'])
        return act
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ActAddTagsView, self).get_context_data(**kwargs)
        # Just an alias for ``form`` context variable
        context['tag_add_form'] = kwargs['form']
        return context
 
    
class ActRemoveTagView(RemoveTagView):
    def get_object(self):
        """
        Returns the ``Act`` instance being un-tagged.
        """
        act = get_object_or_404(Act, pk=self.kwargs.get('act_pk'))        
        return act


class ActTransitionToggleBaseView(FormView):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ActTransitionToggleBaseView, self).dispatch(*args, **kwargs)

    def form_invalid(self, form=None):
        msg = "Invalid transition for this act!"
        return HttpResponseBadRequest(msg)

    def get_success_url(self):
        return self.act.downcast().get_absolute_url()

    def get(self, *args, **kwargs):
        msg = "This view can be accessed only via POST"
        return HttpResponseNotAllowed(msg)


class ActTransitionAddView(ActTransitionToggleBaseView):
    def post(self, request, *args, **kwargs):
        self.act = get_object_or_404(Act, pk=kwargs['pk'])

        if 'votation' in request.POST:
            form = ActFinalTransitionForm(data=request.POST)
            form.fields['final_status'].widget.choices = [('APPROVED','Approvato'),('REJECTED','Rifiutato')]
        else:
            form = ActTransitionForm(data=request.POST)

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
