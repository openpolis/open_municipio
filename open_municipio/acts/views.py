from django.views.generic import DetailView

from open_municipio.acts.models import Act


class ActDetailView(DetailView):
    model = Act
    context_object_name = 'act'
 
