from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.template.context import RequestContext
from django.views.generic import DetailView, FormView, ListView, TemplateView
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.decorators import method_decorator

from django.contrib.auth.decorators import login_required

from open_municipio.taxonomy.models import Tag, Category


class AddTagsView(FormView):
    """
    Abstract class-based view for adding a tagset to a given model instance.
    
    Concrete subclasses MUST specify these class attributes:
    
    * ``form_class``: class of the form used for tagging objects
    * ``template_name``: name of the template used to render the response
    
    and the following instance methods:
    
    * ``get_object()``: should return the model instance being tagged
    
    Moreover, concrete subclasses MAY specify these class attributes:
    
    * ``context_object_name``: the context variable containing the tagged item (default:'tagged_item'): 
    """
    form_class = None
    template_name = None
    context_object_name = 'tagged_item'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AddTagsView, self).dispatch(*args, **kwargs)
    
    def get_object(self):
        """
        Returns the model instance being tagged.
        """
        raise NotImplementedError
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(AddTagsView, self).get_context_data(**kwargs)
        # Just an alias for ``form`` context variable
        context[self.context_object_name] = self.tagged_item
        return context
    
    def get_success_url(self):
        return self.tagged_item.get_absolute_url()
    
    def form_valid(self, form):
        new_tags =  form.cleaned_data['tags']
        self.tagged_item.tag_set.add(*new_tags, tagger=self.request.user)
        return HttpResponseRedirect(self.get_success_url())
    
    def get(self, request, *args, **kwargs):
        self.tagged_item = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context = self.get_context_data(form=form)
        self.render_to_response(context)
        
    def post(self, request, *args, **kwargs):
        self.tagged_item = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
 
    
class RemoveTagView(TemplateView):
    """
    Abstract class-based view for removing a tag from the tagset of a given model instance.
    
    Concrete subclasses MUST specify the following instance method:
    
    * ``get_object()``: should return the model instance being un-tagged
    
    Moreover, concrete subclasses MAY specify this instance method:
    
    *  ``check_perms()``: test to be run in order to check if the user is allowed to remove the tag
                          from the given model instance
        
    """
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(RemoveTagView, self).dispatch(*args, **kwargs)
    
    def get_object(self):
        """
        Returns the model instance being un-tagged.
        """
        raise NotImplementedError
    
    def get_success_url(self):
        return self.tagged_item.get_absolute_url()
        
    def check_perms(self):
        """
        Access control check.
        """ 
        return self.request.user.is_staff
    
    def get(self, request, *args, **kwargs):
        if self.check_perms():
            self.tagged_item = self.get_object()
            tag = get_object_or_404(Tag, slug=kwargs.get('tag_slug'))
            self.tagged_item.tag_set.remove(tag)
            return HttpResponseRedirect(self.get_success_url())
        else: # permission check failed !
            return HttpResponseForbidden


class TopicListView(ListView):
    model = Category
    template_name = 'taxonomy/topic_list.html'
    
    def get_context_data(self, **kwargs):
        # call the base implementation first to get a context
        context = super(TopicListView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        
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
        
        tags = list(Tag.objects.all())
        categories = list(Category.objects.all())
        context['topics'] = tags + categories
                
        return context
    
    
class TagDetailView(TopicDetailView):
    model = Tag
  
    
class CategoryDetailView(TopicDetailView):
    model = Category