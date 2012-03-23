from django.http import HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseRedirect
from django.views.generic import DetailView, ListView, TemplateView
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.edit import FormView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from open_municipio.acts.models import Act, Agenda, Deliberation, Interpellation, Interrogation, Motion
from open_municipio.acts.forms import TagAddForm, ActDescriptionForm
from open_municipio.monitoring.forms import MonitoringForm
from open_municipio.taxonomy.models import Tag
from open_municipio.taxonomy.views import AddTagsView, RemoveTagView

class ActListView(ListView):
    model = Act
    template_name = 'acts/act_list.html'
    queryset = Act.objects.select_subclasses()


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
        if self.request.user.is_authenticated() and \
           self.request.user.get_profile().person and \
           self.request.user.get_profile().person in signers:
            context['description_form'] = ActDescriptionForm(data = {
                'id': act.pk,
                'description': act.description,
            })
        
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
        
        # all arguments
        context['tags'] = Tag.objects.all()

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
