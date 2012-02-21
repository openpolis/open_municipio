from django.views.generic import DetailView, TemplateView


class HomeView(TemplateView):
    template_name = "home.html"

class InfoView(TemplateView):
    template_name = "info.html"
