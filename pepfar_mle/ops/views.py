from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from pepfar_mle.common.views import ApprovedMixin


class VersionsView(LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/ops/versions.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active"] = "facilities-nav"  # id of active nav element
        context["selected"] = "versions"  # id of selected page
        return context


class TicketsView(LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/ops/tickets.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active"] = "facilities-nav"  # id of active nav element
        context["selected"] = "tickets"  # id of selected page
        return context


class ActivityLogView(LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/ops/activity_log.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active"] = "program-nav"  # id of active nav element
        context["selected"] = "activity-log"  # id of selected page
        return context


class SiteMentorshipView(LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/ops/site_mentorship.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active"] = "program-nav"  # id of active nav element
        context["selected"] = "site-mentorship"  # id of selected page
        return context


class DailySiteUpdatesView(LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/ops/daily_site_updates.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active"] = "program-nav"  # id of active nav element
        context["selected"] = "daily-site-updates"  # id of selected page
        return context


class TimeSheetsView(LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/ops/timesheets.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active"] = "program-nav"  # id of active nav element
        context["selected"] = "timesheets"  # id of selected page
        return context