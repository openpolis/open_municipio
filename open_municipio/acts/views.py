from django.views.generic import DetailView, ListView
from django.shortcuts import get_object_or_404

from open_municipio.taxonomy.views import AddTagsView, RemoveTagView  

from open_municipio.acts.models import Act, Agenda, Deliberation, Interpellation, Interrogation, Motion
from open_municipio.acts.forms import TagAddForm

class ActListView(ListView):
    pass

class ActDetailView(DetailView):
    model = Act
    context_object_name = 'act'
    template_name = 'acts/act_detail.html'
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ActDetailView, self).get_context_data(**kwargs)
        # Add in a form for adding tags
        context['tag_add_form'] = TagAddForm()
        return context


class AgendaDetailView(ActDetailView):
    model = Agenda
    context_object_name = 'agenda'
    template_name = 'acts/agenda_detail.html'


class DeliberationDetailView(ActDetailView):
    model = Deliberation
    context_object_name = 'deliberation'
    template_name = 'acts/deliberation_detail.html'


class InterpellationDetailView(ActDetailView):
    model = Interpellation
    context_object_name = 'interpellation'
    template_name = 'acts/interpellation_detail.html'


class InterrogationDetailView(ActDetailView):
    model = Interrogation
    context_object_name = 'interrogation'
    template_name = 'acts/interrogation_detail.html'

class MotionDetailView(ActDetailView):
    model = Motion
    context_object_name = 'motion'
    template_name = 'acts/motion_detail.html'
    

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