from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponseNotAllowed
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, TemplateView
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.edit import FormView
from django.contrib.auth.decorators import login_required

from open_municipio.acts.models import Act, Agenda, Deliberation, Interpellation, Interrogation, Motion, Transition
from open_municipio.acts.forms import TagAddForm, ActTransitionForm, ActFinalTransitionForm
from open_municipio.monitoring.forms import MonitoringForm
from open_municipio.taxonomy.models import Tag, Category
from open_municipio.taxonomy.views import AddTagsView, RemoveTagView

class ActListView(ListView):
    model = Act
    template_name = 'acts/act_list.html'
    queryset = Act.objects.select_subclasses()


class ActEditorView(TemplateView):
    pass


class ActDetailView(DetailView):
    model = Act
    context_object_name = 'act' 
    
    def get_context_data(self, **kwargs):
        act = self.get_object()
        # Call the base implementation first to get a context
        context = super(ActDetailView, self).get_context_data(**kwargs)
        # mix-in tab-related context
        self.tab = self.kwargs.get('tab', 'default')
        extra_context = getattr(self, 'get_related_%(tab)s' % {'tab': self.tab})()
        if extra_context:
            context.update(extra_context)
            
        # Add in a form for adding tags
        context['tag_add_form'] = TagAddForm()
        
        
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
        if self.request.user.has_perm('taxnomy.tag') and self.request.user.has_perm('taxonomy.category'):
            # all categories and tags
            context['act_tags_editor'] = {
                'categories' : Category.objects.all(),
                'tags' : Tag.objects.all()
            }

        # retrieve a dictionary with status and its transitions
        context['transition_groups'] = act.get_transitions_groups()

        context['transition_forms'] = {}
        # some user can set transitions
        if self.request.user.has_perm('acts.transition') : #and context['status_list']
            if len(context['transition_groups']) == 5:
                context['transition_to_council_form'] = ActTransitionForm(initial={'act': act, 'final_status': 'COUNCIL' })
                context['transition_to_commission_form'] = ActTransitionForm(initial={'act': act, 'final_status': 'COMMISSION' })
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
