from django.views.generic import DetailView, TemplateView
from open_municipio.people.models import Institution

class InstitutionDetailView(DetailView):
    context_object_name = "institution"
    model = Institution

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(InstitutionDetailView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the institutions
        context['institution_list'] = Institution.objects.all()
        return context
# Create your views here.
