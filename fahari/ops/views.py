from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, TemplateView, UpdateView

from fahari.common.views import ApprovedMixin, BaseFormMixin, BaseView

from .filters import (
    ActivityLogFilter,
    CommodityFilter,
    DailyUpdateFilter,
    FacilitySystemFilter,
    FacilitySystemTicketFilter,
    SiteMentorshipFilter,
    StockReceiptVerificationFilter,
    TimeSheetFilter,
    WeeklyProgramUpdateFilter,
)
from .forms import (
    ActivityLogForm,
    CommodityForm,
    DailyUpdateForm,
    FacilitySystemForm,
    FacilitySystemTicketForm,
    SiteMentorshipForm,
    StockReceiptVerificationForm,
    TimeSheetForm,
    WeeklyProgramUpdateForm,
)
from .models import (
    ActivityLog,
    Commodity,
    DailyUpdate,
    FacilitySystem,
    FacilitySystemTicket,
    SiteMentorship,
    StockReceiptVerification,
    TimeSheet,
    WeeklyProgramUpdate,
)
from .serializers import (
    ActivityLogSerializer,
    CommoditySerializer,
    DailyUpdateSerializer,
    FacilitySystemSerializer,
    FacilitySystemTicketSerializer,
    SiteMentorshipSerializer,
    StockReceiptVerificationSerializer,
    TimeSheetSerializer,
    WeeklyProgramUpdateSerializer,
)


class FacilitySystemContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # type: ignore
        context["active"] = "facilities-nav"  # id of active nav element
        context["selected"] = "versions"  # id of selected page
        return context


class FacilitySystemsView(
    FacilitySystemContextMixin, LoginRequiredMixin, ApprovedMixin, TemplateView
):
    template_name = "pages/ops/versions.html"
    permission_required = "ops.view_facilitysystem"


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
        context["active"] = "facilities-nav"  # id of active nav element
        context["selected"] = "tickets"  # id of selected page
        return context


class FacilitySystemTicketsView(
    FacilitySystemTicketContextMixin, LoginRequiredMixin, ApprovedMixin, TemplateView
):
    template_name = "pages/ops/tickets.html"
    permission_required = "ops.view_facilitysystemticket"


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


class FacilitySystemTicketResolveView(
    FacilitySystemTicketContextMixin,
    TemplateView,
):
    template_name = "ops/ticket_resolve.html"
    success_url = reverse_lazy("ops:tickets")

    def post(self, request, *args, **kwargs):
        try:
            pk = kwargs["pk"]
            ticket = FacilitySystemTicket.objects.get(pk=pk)
            ticket.resolved_by = str(request.user)
            ticket.resolved = timezone.now()
            ticket.save()
            return HttpResponseRedirect(self.success_url)
        except (FacilitySystemTicket.DoesNotExist, ValidationError, KeyError) as e:
            return render(request, self.template_name, {"errors": [e]})


class FacilitySystemTicketViewSet(BaseView):
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


class StockReceiptVerificationCreateView(
    StockReceiptVerificationContextMixin, BaseFormMixin, CreateView
):
    form_class = StockReceiptVerificationForm
    model = StockReceiptVerification
    success_url = reverse_lazy("ops:stock_receipt_verifications")


class StockReceiptVerificationUpdateView(
    StockReceiptVerificationContextMixin, UpdateView, BaseFormMixin
):
    form_class = StockReceiptVerificationForm
    model = StockReceiptVerification
    success_url = reverse_lazy("ops:stock_receipt_verifications")


class StockReceiptVerificationDeleteView(
    StockReceiptVerificationContextMixin, DeleteView, BaseFormMixin
):
    form_class = StockReceiptVerificationForm
    model = StockReceiptVerification
    success_url = reverse_lazy("ops:stock_receipt_verifications")


class StockReceiptVerificationViewSet(BaseView):
    queryset = StockReceiptVerification.objects.filter(
        active=True,
    )
    serializer_class = StockReceiptVerificationSerializer
    filterset_class = StockReceiptVerificationFilter
    ordering_fields = (
        "facility__name",
        "-expiry_date",
    )
    search_fields = (
        "facility__name",
        "description",
        "comments",
    )


class ActivityLogContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # type: ignore
        context["active"] = "program-nav"  # id of active nav element
        context["selected"] = "activity-log"  # id of selected page
        return context


class ActivityLogView(ActivityLogContextMixin, LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/ops/activity_log.html"
    permission_required = "ops.view_activitylog"


class ActivityLogCreateView(ActivityLogContextMixin, BaseFormMixin, CreateView):
    form_class = ActivityLogForm
    model = ActivityLog
    success_url = reverse_lazy("ops:activity_logs")


class ActivityLogUpdateView(ActivityLogContextMixin, UpdateView, BaseFormMixin):
    form_class = ActivityLogForm
    model = ActivityLog
    success_url = reverse_lazy("ops:activity_logs")


class ActivityLogDeleteView(ActivityLogContextMixin, DeleteView, BaseFormMixin):
    form_class = ActivityLogForm
    model = ActivityLog
    success_url = reverse_lazy("ops:activity_logs")


class ActivityLogViewSet(BaseView):
    queryset = ActivityLog.objects.filter(
        active=True,
    )
    serializer_class = ActivityLogSerializer
    filterset_class = ActivityLogFilter
    ordering_fields = (
        "-planned_date",
        "-requested_date",
        "-procurement_date",
    )
    search_fields = (
        "activity",
        "remarks",
    )


class SiteMentorshipContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # type: ignore
        context["active"] = "program-nav"  # id of active nav element
        context["selected"] = "site-mentorship"  # id of selected page
        return context


class SiteMentorshipView(
    SiteMentorshipContextMixin, LoginRequiredMixin, ApprovedMixin, TemplateView
):
    template_name = "pages/ops/site_mentorship.html"
    permission_required = "ops.view_sitementorship"


class SiteMentorshipCreateView(SiteMentorshipContextMixin, BaseFormMixin, CreateView):
    form_class = SiteMentorshipForm
    model = SiteMentorship
    success_url = reverse_lazy("ops:site_mentorships")


class SiteMentorshipUpdateView(SiteMentorshipContextMixin, UpdateView, BaseFormMixin):
    form_class = SiteMentorshipForm
    model = SiteMentorship
    success_url = reverse_lazy("ops:site_mentorships")


class SiteMentorshipDeleteView(SiteMentorshipContextMixin, DeleteView, BaseFormMixin):
    form_class = SiteMentorshipForm
    model = SiteMentorship
    success_url = reverse_lazy("ops:site_mentorships")


class SiteMentorshipViewSet(BaseView):
    queryset = SiteMentorship.objects.filter(
        active=True,
    )
    serializer_class = SiteMentorshipSerializer
    filterset_class = SiteMentorshipFilter
    ordering_fields = (
        "-day",
        "-end",
        "-start",
        "site__name",
    )
    search_fields = (
        "staff_member__name",
        "site__name",
        "objective",
    )


class DailySiteUpdatesContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # type: ignore
        context["active"] = "program-nav"  # id of active nav element
        context["selected"] = "daily-site-updates"  # id of selected page
        return context


class DailySiteUpdatesView(
    DailySiteUpdatesContextMixin, LoginRequiredMixin, ApprovedMixin, TemplateView
):
    template_name = "pages/ops/daily_site_updates.html"
    permission_required = "ops.view_dailyupdate"


class DailyUpdateCreateView(DailySiteUpdatesContextMixin, BaseFormMixin, CreateView):
    form_class = DailyUpdateForm
    model = DailyUpdate
    success_url = reverse_lazy("ops:daily_site_updates")


class DailyUpdateUpdateView(DailySiteUpdatesContextMixin, UpdateView, BaseFormMixin):
    form_class = DailyUpdateForm
    model = DailyUpdate
    success_url = reverse_lazy("ops:daily_site_updates")


class DailyUpdateDeleteView(DailySiteUpdatesContextMixin, DeleteView, BaseFormMixin):
    form_class = DailyUpdateForm
    model = DailyUpdate
    success_url = reverse_lazy("ops:daily_site_updates")


class DailyUpdateViewSet(BaseView):
    queryset = DailyUpdate.objects.filter(
        active=True,
    )
    serializer_class = DailyUpdateSerializer
    filterset_class = DailyUpdateFilter
    ordering_fields = (
        "-date",
        "facility__name",
    )
    search_fields = ("facility__name",)


class TimeSheetContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # type: ignore
        context["active"] = "program-nav"  # id of active nav element
        context["selected"] = "timesheets"  # id of selected page
        return context


class TimeSheetsView(TimeSheetContextMixin, LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/ops/timesheets.html"
    permission_required = "ops.view_timesheet"


class TimeSheetCreateView(TimeSheetContextMixin, BaseFormMixin, CreateView):
    form_class = TimeSheetForm
    model = TimeSheet
    success_url = reverse_lazy("ops:timesheets")


class TimeSheetUpdateView(TimeSheetContextMixin, UpdateView, BaseFormMixin):
    form_class = TimeSheetForm
    model = TimeSheet
    success_url = reverse_lazy("ops:timesheets")


class TimeSheetDeleteView(TimeSheetContextMixin, DeleteView, BaseFormMixin):
    form_class = TimeSheetForm
    model = TimeSheet
    success_url = reverse_lazy("ops:timesheets")


class TimeSheetApproveView(TimeSheetContextMixin, TemplateView):
    template_name = "ops/timesheet_approve.html"
    success_url = reverse_lazy("ops:timesheets")

    def post(self, request, *args, **kwargs):
        try:
            pk = kwargs["pk"]
            timesheet = TimeSheet.objects.get(pk=pk)
            timesheet.approved_by = request.user
            timesheet.approved_at = timezone.now()
            timesheet.save()
            return HttpResponseRedirect(self.success_url)
        except (TimeSheet.DoesNotExist, ValidationError, KeyError) as e:
            return render(request, self.template_name, {"errors": [e]})


class TimeSheetViewSet(BaseView):
    queryset = TimeSheet.objects.filter(
        active=True,
    )
    serializer_class = TimeSheetSerializer
    filterset_class = TimeSheetFilter
    ordering_fields = (
        "-date",
        "-approved_at",
        "staff__name",
    )
    search_fields = (
        "staff__name",
        "activity",
        "output",
        "location",
    )


class WeeklyProgramUpdateContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # type: ignore
        context["active"] = "program-nav"  # id of active nav element
        context["selected"] = "weekly-program-updates"  # id of selected page
        return context


class WeeklyProgramUpdatesView(
    WeeklyProgramUpdateContextMixin, LoginRequiredMixin, ApprovedMixin, TemplateView
):
    template_name = "pages/ops/weekly_program_updates.html"
    permission_required = (
        "ops.view_weeklyprogramupdate",
        "ops.view_activity",
        "ops.view_operationalarea",
    )


class WeeklyProgramUpdatesCreateView(WeeklyProgramUpdateContextMixin, BaseFormMixin, CreateView):
    form_class = WeeklyProgramUpdateForm
    model = WeeklyProgramUpdate
    success_url = reverse_lazy("ops:weekly_program_updates")


class WeeklyProgramUpdatesUpdateView(WeeklyProgramUpdateContextMixin, UpdateView, BaseFormMixin):
    form_class = WeeklyProgramUpdateForm
    model = WeeklyProgramUpdate
    success_url = reverse_lazy("ops:weekly_program_updates")


class WeeklyProgramUpdatesDeleteView(WeeklyProgramUpdateContextMixin, DeleteView, BaseFormMixin):
    form_class = WeeklyProgramUpdateForm
    model = WeeklyProgramUpdate
    success_url = reverse_lazy("ops:weekly_program_updates")


class WeeklyProgramUpdateViewSet(BaseView):
    queryset = WeeklyProgramUpdate.objects.filter(
        active=True,
    )
    serializer_class = WeeklyProgramUpdateSerializer
    filterset_class = WeeklyProgramUpdateFilter
    ordering_fields = ("-date",)
    search_fields = (
        "activity__name",
        "comments",
    )


class CommodityContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # type: ignore
        context["active"] = "program-nav"  # id of active nav element
        context["selected"] = "commodities"  # id of selected page
        return context


class CommoditiesListView(CommodityContextMixin, LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/ops/commodities.html"
    permission_required = ("ops.view_commodity",)


class CommodityCreateView(CommodityContextMixin, BaseFormMixin, CreateView):
    form_class = CommodityForm
    model = Commodity
    success_url = reverse_lazy("ops:commodities")


class CommodityUpdateView(CommodityContextMixin, UpdateView, BaseFormMixin):
    form_class = CommodityForm
    model = Commodity
    success_url = reverse_lazy("ops:commodities")


class CommodityDeleteView(CommodityContextMixin, DeleteView, BaseFormMixin):
    form_class = CommodityForm
    model = Commodity
    success_url = reverse_lazy("ops:commodities")


class CommodityViewSet(BaseView):
    queryset = Commodity.objects.filter(
        active=True,
    )
    serializer_class = CommoditySerializer
    filterset_class = CommodityFilter
    ordering_fields = (
        "name",
        "code",
    )
    search_fields = (
        "name",
        "code",
        "description",
    )
