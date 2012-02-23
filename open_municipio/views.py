from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = 'om/home.html'

class InfoView(TemplateView):
    template_name = 'om/info.html'

