from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from pepfar_mle.common.views import ApprovedMixin


class VersionsView(LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/ops/versions.html"


class TicketsView(LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/ops/tickets.html"


class ActivityLogView(LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/ops/activity_log.html"


class SiteMentorshipView(LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/ops/site_mentorship.html"


class DailySiteUpdatesView(LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/ops/daily_site_updates.html"


class TimeSheetsView(LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/ops/timesheets.html"
