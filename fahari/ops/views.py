from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, TemplateView, UpdateView

from fahari.common.views import ApprovedMixin, BaseFormMixin, BaseView

from .filters import FacilitySystemFilter, FacilitySystemTicketFilter
from .forms import FacilitySystemForm, FacilitySystemTicketForm
from .models import FacilitySystem, FacilitySystemTicket
from .serializers import FacilitySystemSerializer, FacilitySystemTicketSerializer


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


class FacilitySystemContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # type: ignore
        context["active"] = "program-nav"  # id of active nav element
        context["selected"] = "versions"  # id of selected page
        return context


class FacilitySystemsView(
    FacilitySystemContextMixin, LoginRequiredMixin, ApprovedMixin, TemplateView
):
    template_name = "pages/ops/versions.html"
    permission_required = "ops.view_facility_system"


class FacilitySystemCreateView(FacilitySystemContextMixin, BaseFormMixin, CreateView):
    form_class = FacilitySystemForm
    success_url = reverse_lazy("ops:versions")
    model = FacilitySystem


class FacilitySystemUpdateView(FacilitySystemContextMixin, UpdateView, BaseFormMixin):
    form_class = FacilitySystemForm
    model = FacilitySystem
    success_url = reverse_lazy("ops:versions")


class FacilitySystemDeleteView(FacilitySystemContextMixin, DeleteView, BaseFormMixin):
    form_class = FacilitySystemForm
    model = FacilitySystem
    success_url = reverse_lazy("ops:versions")


class FacilitySystemViewSet(BaseView):
    permissions = {
        "GET": ["ops.view_facility_system"],
        "POST": ["ops.add_facility_system"],
        "PATCH": ["ops.change_facility_system"],
        "DELETE": ["ops.delete_facility_system"],
    }
    queryset = FacilitySystem.objects.filter(
        active=True,
    )
    serializer_class = FacilitySystemSerializer
    filterset_class = FacilitySystemFilter
    ordering_fields = (
        "facility__name",
        "system__name",
        "-version",
    )
    search_fields = (
        "facility__name",
        "system__name",
        "-version",
    )


class FacilitySystemTicketContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # type: ignore
        context["active"] = "program-nav"  # id of active nav element
        context["selected"] = "tickets"  # id of selected page
        return context


class FacilitySystemTicketsView(
    FacilitySystemTicketContextMixin, LoginRequiredMixin, ApprovedMixin, TemplateView
):
    template_name = "pages/ops/tickets.html"
    permission_required = "ops.view_facility_system_ticket"


class FacilitySystemTicketCreateView(FacilitySystemTicketContextMixin, BaseFormMixin, CreateView):
    form_class = FacilitySystemTicketForm
    success_url = reverse_lazy("ops:tickets")
    model = FacilitySystemTicket


class FacilitySystemTicketUpdateView(FacilitySystemTicketContextMixin, UpdateView, BaseFormMixin):
    form_class = FacilitySystemTicketForm
    model = FacilitySystemTicket
    success_url = reverse_lazy("ops:tickets")


class FacilitySystemTicketDeleteView(FacilitySystemTicketContextMixin, DeleteView, BaseFormMixin):
    form_class = FacilitySystemTicketForm
    model = FacilitySystemTicket
    success_url = reverse_lazy("ops:tickets")


class FacilitySystemTicketViewSet(BaseView):
    permissions = {
        "GET": ["ops.view_facility_system_ticket"],
        "POST": ["ops.add_facility_system_ticket"],
        "PATCH": ["ops.change_facility_system_ticket"],
        "DELETE": ["ops.delete_facility_system_ticket"],
    }
    queryset = FacilitySystemTicket.objects.filter(
        active=True,
    )
    serializer_class = FacilitySystemTicketSerializer
    filterset_class = FacilitySystemTicketFilter
    ordering_fields = (
        "facility_system__facility__name",
        "facility_system__system__name",
        "-raised",
        "-resolved",
    )
    search_fields = (
        "facility_system__facility__name",
        "facility_system__system__name",
    )


class StockReceiptVerificationContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # type: ignore
        context["active"] = "program-nav"  # id of active nav element
        context["selected"] = "stock-receipt-verification"  # id of selected page
        return context


class StockReceiptVerificationView(
    StockReceiptVerificationContextMixin, LoginRequiredMixin, ApprovedMixin, TemplateView
):
    template_name = "pages/ops/stock_receipt_verification.html"
    permission_required = "ops.view_stockreceiptverification"
