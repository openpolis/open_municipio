from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = 'home.html'

class InfoView(TemplateView):
    template_name = 'om/info.html'

