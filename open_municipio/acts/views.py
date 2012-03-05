from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.views.generic import DetailView, FormView, ListView, TemplateView
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator

from django.contrib.auth.decorators import login_required

from taggit.models import Tag

from open_municipio.acts.models import Act
from open_municipio.acts.forms import TagAddForm

class ActListView(ListView):
    pass

class ActEditorView(TemplateView):
    pass

class ActDetailView(DetailView):
    model = Act
    context_object_name = 'act'
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ActDetailView, self).get_context_data(**kwargs)
        # Add in a form for adding tags
        context['tag_add_form'] = TagAddForm()
        return context


class ActAddTagsView(FormView):
    form_class = TagAddForm
    template_name = 'acts/act_detail.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ActAddTagsView, self).dispatch(*args, **kwargs)
    
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
        context['act'] = self.act
        return context
    
    def get_success_url(self):
        return self.act.get_absolute_url()
    
    def form_valid(self, form):
        new_tags =  form.cleaned_data['tags']
        self.act.tag_set.add(*new_tags, tagger=self.request.user)
        return HttpResponseRedirect(self.get_success_url())
    
    def get(self, request, *args, **kwargs):
        self.act = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context = self.get_context_data(form=form)
        self.render_to_response(context)
        
    def post(self, request, *args, **kwargs):
        self.act = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
 
    
class ActRemoveTagView(TemplateView):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ActRemoveTagView, self).dispatch(*args, **kwargs)
    
    def check_perms(self): 
        return self.request.user.is_staff
    
    def get(self, request, *args, **kwargs):
        if self.check_perms():
            act = get_object_or_404(Act, pk=kwargs.get('act_pk'))
            tag = get_object_or_404(Tag, slug=kwargs.get('tag_slug'))
            act.tag_set.remove(tag)
            return HttpResponseRedirect(act.get_absolute_url())
        else: # permission check failed !
            return HttpResponseForbidden
