from django.views.generic import DetailView, TemplateView
from open_municipio.acts.models import Act


class ActDetailView(DetailView):
    context_object_name = "act"
    model = Act

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ActDetailView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the institutions
        context['request'] = self.request
        return context
