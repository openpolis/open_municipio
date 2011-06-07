from django.views.generic import DetailView
from om.models import Institution

class InstitutionDetailView(DetailView):

    context_object_name = "institution"
    model = Institution

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(InstitutionDetailView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['institutions_list'] = Institution.objects.all()
        return context
