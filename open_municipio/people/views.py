from django.views.generic import DetailView

from open_municipio.people.models import Institution


class InstitutionDetailView(DetailView):
    model = Institution
    context_object_name = 'institution'
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(InstitutionDetailView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the institutions
        context['institution_list'] = Institution.objects.all()
        return context

