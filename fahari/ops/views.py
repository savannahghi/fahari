from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, TemplateView, UpdateView

from fahari.common.views import ApprovedMixin, BaseFormMixin, BaseView

from .filters import (
    ActivityLogFilter,
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
        context["active"] = "program-nav"  # id of active nav element
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
    permissions = {
        "GET": ["ops.view_facilitysystem"],
        "POST": ["ops.add_facilitysystem"],
        "PATCH": ["ops.change_facilitysystem"],
        "DELETE": ["ops.delete_facilitysystem"],
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


class FacilitySystemTicketViewSet(BaseView):
    permissions = {
        "GET": ["ops.view_facilitysystemticket"],
        "POST": ["ops.add_facilitysystemticket"],
        "PATCH": ["ops.change_facilitysystemticket"],
        "DELETE": ["ops.delete_facilitysystemticket"],
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
    permissions = {
        "GET": ["ops.view_stockreceiptverification"],
        "POST": ["ops.add_stockreceiptverification"],
        "PATCH": ["ops.change_stockreceiptverification"],
        "DELETE": ["ops.delete_stockreceiptverification"],
    }
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
    permissions = {
        "GET": ["ops.view_activitylog"],
        "POST": ["ops.add_activitylog"],
        "PATCH": ["ops.change_activitylog"],
        "DELETE": ["ops.delete_activitylog"],
    }
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
    permissions = {
        "GET": ["ops.view_sitementorship"],
        "POST": ["ops.add_sitementorship"],
        "PATCH": ["ops.change_sitementorship"],
        "DELETE": ["ops.delete_sitementorship"],
    }
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
    permissions = {
        "GET": ["ops.view_dailyupdate"],
        "POST": ["ops.add_dailyupdate"],
        "PATCH": ["ops.change_dailyupdate"],
        "DELETE": ["ops.delete_dailyupdate"],
    }
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


class TimeSheetViewSet(BaseView):
    permissions = {
        "GET": ["ops.view_timesheet"],
        "POST": ["ops.add_timesheet"],
        "PATCH": ["ops.change_timesheet"],
        "DELETE": ["ops.delete_timesheet"],
    }
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
    permissions = {
        "GET": ["ops.view_weeklyprogramupdate"],
        "POST": ["ops.add_weeklyprogramupdate"],
        "PATCH": ["ops.change_weeklyprogramupdate"],
        "DELETE": ["ops.delete_weeklyprogramupdate"],
    }
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
