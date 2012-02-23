from django.http import HttpResponseRedirect
from django.views.generic import DetailView, TemplateView
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response

from taggit.models import Tag

from open_municipio.acts.models import Act
from open_municipio.acts.forms import TagAddForm


class ActDetailView(DetailView):
    model = Act
    context_object_name = 'act'
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ActDetailView, self).get_context_data(**kwargs)
        # Add in a form for adding tags
        context['tag_add_form'] = TagAddForm()
        return context

# FIXME: convert to a CBV
def add_tags_to_act(request, pk):
    act = get_object_or_404(Act, pk=pk)
    if request.method == 'POST': 
        form = TagAddForm(request.POST) 
        if form.is_valid():
            new_tags =  form.cleaned_data['tags']
            act.tag_set.add(*new_tags, tagger=request.user)
            return HttpResponseRedirect(act.get_absolute_url()) 
    else:
        form = TagAddForm() 

    return render_to_response('acts/act_detail.html', 
                              {'act': act, 'tag_add_form': form,},
                              context_instance=RequestContext(request))
    
    
class ActRemoveTagView(TemplateView):
    def get(self, request, *args, **kwargs):
        act = get_object_or_404(Act, pk=kwargs.get('act_pk'))
        tag = get_object_or_404(Tag, slug=kwargs.get('tag_slug'))
        act.tag_set.remove(tag)
        return HttpResponseRedirect(act.get_absolute_url())
