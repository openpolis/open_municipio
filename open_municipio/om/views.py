from django.views.generic.base import TemplateView
from open_municipio.acts.models import Calendar, Act

class HomeView(TemplateView):
    template_name = "om/home.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(HomeView, self).get_context_data(**kwargs)

        # get last two calendar events

        context['events'] = Calendar.objects.all().order_by('date')[0:2]
        context['key_acts'] = Act.objects.filter(is_key=True).order_by('-presentation_date')[0:3]
        return context

    
