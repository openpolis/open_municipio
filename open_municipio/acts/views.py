from django.http import HttpResponseRedirect
from django.views.generic import DetailView, TemplateView
from django.shortcuts import get_object_or_404, render_to_response

from open_municipio.taxonomy.models import Tag

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
    if request.method == 'POST': 
        form = TagAddForm(request.POST) 
        if form.is_valid():
            act = get_object_or_404(Act, pk=pk)
            new_tags =  form.cleaned_data['tags']
            act.tag_set.add(*new_tags)
            # FIXME: hardcoded URL !
            return HttpResponseRedirect('/acts/%s/' % act.pk) 
    else:
        form = TagAddForm() 

    return render_to_response('acts/act_detail.html', {
        'form': form,
    })
    
    
class ActRemoveTagView(TemplateView):
    def get(self, request, *args, **kwargs):
        act = get_object_or_404(Act, pk=kwargs.get('act_pk'))
        tag = get_object_or_404(Tag, slug=kwargs.get('tag_slug'))
        act.tag_set.remove(tag)
        # FIXME: hardcoded URL !
        return HttpResponseRedirect('/acts/%s/' % act.pk)
    
    