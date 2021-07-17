from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, View


class ApprovedMixin(UserPassesTestMixin, View):
    permission_denied_message = "Your account is pending approval"

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_approved


class HomeView(LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active"] = "dashboard-nav"  # id of active nav element
        return context


class AboutView(LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active"] = "dashboard-nav"  # id of active nav element
        return context


class FacilityView(LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/common/facilities.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active"] = "facilities-nav"  # id of active nav element
        context["selected"] = "facilities"  # id of selected page
        return context


class SystemsView(LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/common/systems.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active"] = "facilities-nav"  # id of active nav element
        context["selected"] = "systems"  # id of selected page
        return context
