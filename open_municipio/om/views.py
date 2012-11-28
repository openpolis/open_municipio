from django.conf import settings
from django.views.generic.base import TemplateView
from open_municipio.acts.models import Calendar, Act

from django import http
from django.template import (Context, loader)


def server_error(request, template_name='500.html'):
    """
    500 error handler.

    Templates: `500.html`
    Context: None
    """
    c = Context({
        'STATIC_URL':settings.STATIC_URL,
        'main_city': settings.SITE_INFO['main_city']
    })
    t = loader.get_template(template_name) # You need to create a 500.html template.
    return http.HttpResponseServerError(t.render(c))

class HomeView(TemplateView):
    template_name = "om/home.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(HomeView, self).get_context_data(**kwargs)

        # get last two calendar events

        context['events'] = Calendar.objects.all().order_by('date')[0:2]
        context['key_acts'] = Act.objects.filter(is_key=True).order_by('-presentation_date')[0:3]
        return context

    
