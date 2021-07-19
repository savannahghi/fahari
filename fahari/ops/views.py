from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from fahari.common.views import ApprovedMixin


class VersionsView(LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/ops/versions.html"
    permission_required = "ops.view_facilitysystem"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active"] = "facilities-nav"  # id of active nav element
        context["selected"] = "versions"  # id of selected page
        return context


class TicketsView(LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/ops/tickets.html"
    permission_required = "ops.view_facilitysystemticket"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active"] = "facilities-nav"  # id of active nav element
        context["selected"] = "tickets"  # id of selected page
        return context


class TimeSheetsView(LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/ops/timesheets.html"
    permission_required = "ops.view_timesheet"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active"] = "program-nav"  # id of active nav element
        context["selected"] = "timesheets"  # id of selected page
        return context


class ActivityLogView(LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/ops/activity_log.html"
    permission_required = "ops.view_activitylog"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active"] = "program-nav"  # id of active nav element
        context["selected"] = "activity-log"  # id of selected page
        return context


class SiteMentorshipView(LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/ops/site_mentorship.html"
    permission_required = "ops.view_sitementorship"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active"] = "program-nav"  # id of active nav element
        context["selected"] = "site-mentorship"  # id of selected page
        return context


class DailySiteUpdatesView(LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/ops/daily_site_updates.html"
    permission_required = "ops.view_dailyupdate"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active"] = "program-nav"  # id of active nav element
        context["selected"] = "daily-site-updates"  # id of selected page
        return context


class WeeklyProgramUpdatesView(LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/ops/weekly_program_updates.html"
    permission_required = (
        "ops.view_weeklyprogramupdate",
        "ops.view_activity",
        "ops.view_operationalarea",
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active"] = "program-nav"  # id of active nav element
        context["selected"] = "weekly-program-updates"  # id of selected page
        return context
