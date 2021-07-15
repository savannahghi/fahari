from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "pages/home.html"


class AboutView(LoginRequiredMixin, TemplateView):
    template_name = "pages/about.html"
