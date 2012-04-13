from django.views.generic import DetailView, ListView

from open_municipio.taxonomy.models import Tag, Category



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

        context['topics'] = Category.objects.all()
                
        return context
    
    
class TagDetailView(TopicDetailView):
    model = Tag
  
    
class CategoryDetailView(TopicDetailView):
    model = Category