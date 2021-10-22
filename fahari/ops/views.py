from typing import cast

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, TemplateView, UpdateView
from django.views.generic.detail import SingleObjectMixin, SingleObjectTemplateResponseMixin
from django.views.generic.edit import FormMixin, ProcessFormView

from fahari.common.views import ApprovedMixin, BaseFormMixin, BaseView, FormContextMixin
from fahari.misc.forms import ImportStockVerificationReceiptsForm

from .filters import (
    ActivityLogFilter,
    CommodityFilter,
    DailyUpdateFilter,
    FacilityDeviceFilter,
    FacilityDeviceRequestFilter,
    FacilityNetworkStatusFilter,
    FacilitySystemFilter,
    FacilitySystemTicketFilter,
    QuestionFilter,
    QuestionGroupFilter,
    QuestionnaireFilter,
    SecurityIncidenceFilter,
    SiteMentorshipFilter,
    StockReceiptVerificationFilter,
    TimeSheetFilter,
    UoMCategoryFilter,
    UoMFilter,
    WeeklyProgramUpdateCommentsFilter,
    WeeklyProgramUpdateFilter,
)
from .forms import (
    ActivityLogForm,
    CommodityForm,
    DailyUpdateForm,
    FacilityDeviceForm,
    FacilityDeviceRequestForm,
    FacilityNetworkStatusForm,
    FacilitySystemForm,
    FacilitySystemTicketForm,
    FacilitySystemTicketResolveForm,
    QuestionForm,
    QuestionGroupForm,
    QuestionnaireForm,
    SecurityIncidenceForm,
    SiteMentorshipForm,
    StockReceiptVerificationForm,
    TimeSheetForm,
    UoMCategoryForm,
    UoMForm,
    WeeklyProgramUpdateCommentForm,
    WeeklyProgramUpdateForm,
)
from .models import (
    ActivityLog,
    Commodity,
    DailyUpdate,
    FacilityDevice,
    FacilityDeviceRequest,
    FacilityNetworkStatus,
    FacilitySystem,
    FacilitySystemTicket,
    Question,
    QuestionGroup,
    Questionnaire,
    SecurityIncidence,
    SiteMentorship,
    StockReceiptVerification,
    TimeSheet,
    UoM,
    UoMCategory,
    WeeklyProgramUpdate,
    WeeklyProgramUpdateComment,
)
from .serializers import (
    ActivityLogSerializer,
    CommoditySerializer,
    DailyUpdateSerializer,
    FacilityDeviceRequestSerializer,
    FacilityDeviceSerializer,
    FacilityNetworkStatusSerializer,
    FacilitySystemSerializer,
    FacilitySystemTicketSerializer,
    QuestionGroupSerializer,
    QuestionnaireSerializer,
    QuestionSerializer,
    SecurityIncidenceSerializer,
    SiteMentorshipSerializer,
    StockReceiptVerificationSerializer,
    TimeSheetSerializer,
    UoMCategorySerializer,
    UoMSerializer,
    WeeklyProgramUpdateCommentsReadSerializer,
    WeeklyProgramUpdateSerializer,
)


class FacilitySystemContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # type: ignore
        context["active"] = "facilities-nav"  # id of active nav element
        context["available_fields_url"] = reverse_lazy("api:facilitysystem-get-available-fields")
        context["dump_data_url"] = reverse_lazy("api:facilitysystem-dump-data")
        context["get_filter_form_url"] = reverse_lazy("api:facilitysystem-get-filter-form")
        context["selected"] = "versions"  # id of selected page
        return context


class FacilitySystemsView(
    FacilitySystemContextMixin, LoginRequiredMixin, ApprovedMixin, TemplateView
):
    template_name = "pages/ops/versions.html"
    permission_required = "ops.view_facilitysystem"


class FacilitySystemCreateView(
    FacilitySystemContextMixin, FormContextMixin, BaseFormMixin, CreateView
):

    form_class = FacilitySystemForm
    success_url = reverse_lazy("ops:versions")
    model = FacilitySystem


class FacilitySystemUpdateView(
    FacilitySystemContextMixin, FormContextMixin, UpdateView, BaseFormMixin
):
    form_class = FacilitySystemForm
    model = FacilitySystem
    success_url = reverse_lazy("ops:versions")


class FacilitySystemDeleteView(
    FacilitySystemContextMixin, FormContextMixin, DeleteView, BaseFormMixin
):
    form_class = FacilitySystemForm
    model = FacilitySystem
    success_url = reverse_lazy("ops:versions")


class FacilitySystemViewSet(BaseView):
    queryset = FacilitySystem.objects.active()
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
    facility_field_lookup = "facility"


class FacilitySystemTicketContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # type: ignore
        context["active"] = "facilities-nav"  # id of active nav element
        context["available_fields_url"] = reverse_lazy(
            "api:facilitysystemticket-get-available-fields"
        )
        context["dump_data_url"] = reverse_lazy("api:facilitysystemticket-dump-data")
        context["get_filter_form_url"] = reverse_lazy("api:facilitysystemticket-get-filter-form")
        context["selected"] = "tickets"  # id of selected page
        return context


class FacilitySystemTicketsView(
    FacilitySystemTicketContextMixin, LoginRequiredMixin, ApprovedMixin, TemplateView
):
    template_name = "pages/ops/tickets.html"
    permission_required = "ops.view_facilitysystemticket"


class FacilitySystemTicketCreateView(
    FacilitySystemTicketContextMixin, BaseFormMixin, FormContextMixin, CreateView
):
    form_class = FacilitySystemTicketForm
    model = FacilitySystemTicket
    success_url = reverse_lazy("ops:tickets")


class FacilitySystemTicketUpdateView(
    FacilitySystemTicketContextMixin, BaseFormMixin, FormContextMixin, UpdateView
):
    form_class = FacilitySystemTicketForm
    model = FacilitySystemTicket
    success_url = reverse_lazy("ops:tickets")


class FacilitySystemTicketDeleteView(
    FacilitySystemTicketContextMixin, BaseFormMixin, FormContextMixin, DeleteView
):
    form_class = FacilitySystemTicketForm
    model = FacilitySystemTicket
    success_url = reverse_lazy("ops:tickets")


class FacilitySystemTicketResolveView(
    FacilitySystemTicketContextMixin,
    ProcessFormView,
    FormMixin,
    SingleObjectMixin,
    SingleObjectTemplateResponseMixin,
):
    form_class = FacilitySystemTicketResolveForm
    model = FacilitySystemTicket
    template_name = "ops/ticket_resolve.html"
    success_url = reverse_lazy("ops:tickets")

    def form_valid(self, form):
        ticket: FacilitySystemTicket = cast(FacilitySystemTicket, self.get_object())
        ticket.resolved_by = str(self.request.user)
        ticket.resolved = timezone.now()
        ticket.resolve_note = form.cleaned_data["resolve_note"]
        ticket.save()
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        # noinspection PyAttributeOutsideInit
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_initial(self):
        initial = super().get_initial()
        ticket: FacilitySystemTicket = cast(FacilitySystemTicket, self.get_object())
        initial.update({"resolve_note": ticket.resolve_note})
        return initial


class FacilitySystemTicketViewSet(BaseView):
    queryset = FacilitySystemTicket.objects.active()
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
    facility_field_lookup = "facility_system__facility"


class StockReceiptVerificationContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # type: ignore
        context["active"] = "inventory-nav"  # id of active nav element
        context["available_fields_url"] = reverse_lazy(
            "api:stockreceiptverification-get-available-fields"
        )
        context["dump_data_url"] = reverse_lazy("api:stockreceiptverification-dump-data")
        context["get_filter_form_url"] = reverse_lazy(
            "api:stockreceiptverification-get-filter-form"
        )
        context["selected"] = "stock-receipt-verifications"  # id of selected page
        context["ingest_form"] = ImportStockVerificationReceiptsForm()
        return context


class StockReceiptVerificationView(
    StockReceiptVerificationContextMixin, LoginRequiredMixin, ApprovedMixin, TemplateView
):
    template_name = "pages/ops/stock_receipt_verification.html"
    permission_required = "ops.view_stockreceiptverification"


class StockReceiptVerificationCreateView(
    StockReceiptVerificationContextMixin, BaseFormMixin, FormContextMixin, CreateView
):
    form_class = StockReceiptVerificationForm
    model = StockReceiptVerification
    success_url = reverse_lazy("ops:stock_receipt_verifications")


class StockReceiptVerificationUpdateView(
    StockReceiptVerificationContextMixin, BaseFormMixin, FormContextMixin, UpdateView
):
    form_class = StockReceiptVerificationForm
    model = StockReceiptVerification
    success_url = reverse_lazy("ops:stock_receipt_verifications")


class StockReceiptVerificationDeleteView(
    StockReceiptVerificationContextMixin, BaseFormMixin, FormContextMixin, DeleteView
):
    form_class = StockReceiptVerificationForm
    model = StockReceiptVerification
    success_url = reverse_lazy("ops:stock_receipt_verifications")


class StockReceiptVerificationViewSet(BaseView):
    queryset = StockReceiptVerification.objects.active()
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
    facility_field_lookup = "facility"


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
    queryset = ActivityLog.objects.active()
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


class SiteMentorshipCreateView(
    SiteMentorshipContextMixin, BaseFormMixin, FormContextMixin, CreateView
):
    form_class = SiteMentorshipForm
    model = SiteMentorship
    success_url = reverse_lazy("ops:site_mentorships")


class SiteMentorshipUpdateView(
    SiteMentorshipContextMixin, BaseFormMixin, FormContextMixin, UpdateView
):
    form_class = SiteMentorshipForm
    model = SiteMentorship
    success_url = reverse_lazy("ops:site_mentorships")


class SiteMentorshipDeleteView(
    SiteMentorshipContextMixin, BaseFormMixin, FormContextMixin, DeleteView
):
    form_class = SiteMentorshipForm
    model = SiteMentorship
    success_url = reverse_lazy("ops:site_mentorships")


class SiteMentorshipViewSet(BaseView):
    queryset = SiteMentorship.objects.active()
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
    facility_field_lookup = "site"


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


class DailyUpdateCreateView(
    DailySiteUpdatesContextMixin, BaseFormMixin, FormContextMixin, CreateView
):
    form_class = DailyUpdateForm
    model = DailyUpdate
    success_url = reverse_lazy("ops:daily_site_updates")


class DailyUpdateUpdateView(
    DailySiteUpdatesContextMixin, BaseFormMixin, FormContextMixin, UpdateView
):
    form_class = DailyUpdateForm
    model = DailyUpdate
    success_url = reverse_lazy("ops:daily_site_updates")


class DailyUpdateDeleteView(
    DailySiteUpdatesContextMixin, BaseFormMixin, FormContextMixin, DeleteView
):
    form_class = DailyUpdateForm
    model = DailyUpdate
    success_url = reverse_lazy("ops:daily_site_updates")


class DailyUpdateViewSet(BaseView):
    queryset = DailyUpdate.objects.active()
    serializer_class = DailyUpdateSerializer
    filterset_class = DailyUpdateFilter
    ordering_fields = (
        "-date",
        "facility__name",
    )
    search_fields = ("facility__name",)
    facility_field_lookup = "facility"


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
    queryset = TimeSheet.objects.active()
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
    )


class WeeklyProgramUpdatesCreateView(WeeklyProgramUpdateContextMixin, BaseFormMixin, CreateView):
    form_class = WeeklyProgramUpdateForm
    model = WeeklyProgramUpdate
    success_url = reverse_lazy("ops:weekly_program_updates")


class WeeklyProgramUpdatesUpdateView(WeeklyProgramUpdateContextMixin, UpdateView, BaseFormMixin):
    form_class = WeeklyProgramUpdateForm
    model = WeeklyProgramUpdate
    success_url = reverse_lazy("ops:weekly_program_updates")

    def get_context_data(self, **kwargs):
        program_update: WeeklyProgramUpdate = self.object  # type: ignore
        context = super().get_context_data(**kwargs)
        create_comments_form = WeeklyProgramUpdateCommentForm(
            initial={
                "organisation": program_update.organisation.pk,
                "weekly_update": program_update.pk,
            }
        )
        create_comments_form.fields["weekly_update"].queryset = WeeklyProgramUpdate.objects.filter(
            pk=program_update.pk
        )
        create_comments_form.helper.form_action = reverse_lazy(
            "ops:weekly_program_update_comments_create"
        )
        context["create_comments_form"] = create_comments_form
        return context


class WeeklyProgramUpdatesDeleteView(WeeklyProgramUpdateContextMixin, DeleteView, BaseFormMixin):
    form_class = WeeklyProgramUpdateForm
    model = WeeklyProgramUpdate
    success_url = reverse_lazy("ops:weekly_program_updates")


class WeeklyProgramUpdateViewSet(BaseView):
    queryset = WeeklyProgramUpdate.objects.active()
    filterset_class = WeeklyProgramUpdateFilter
    serializer_class = WeeklyProgramUpdateSerializer
    ordering_fields = ("-date_created",)
    search_fields = (
        "title",
        "operation_area",
        "status",
    )


class WeeklyProgramUpdateCommentsContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # type: ignore
        context["active"] = "program-nav"  # id of active nav element
        context["selected"] = "weekly-program-update-comments"  # id of selected page
        return context


class WeeklyProgramUpdateCommentsView(
    WeeklyProgramUpdateCommentsContextMixin, LoginRequiredMixin, ApprovedMixin, TemplateView
):
    template_name = "pages/ops/weekly_program_update_comments.html"
    permission_required = (
        "ops.view_activity",
        "ops.view_WeeklyProgramUpdateComment",
    )


class WeeklyProgramUpdatesCommentCreateView(
    WeeklyProgramUpdateCommentsContextMixin, CreateView, BaseFormMixin
):
    form_class = WeeklyProgramUpdateCommentForm
    model = WeeklyProgramUpdateComment

    def get_success_url(self):
        weekly_comment: WeeklyProgramUpdateComment = self.object  # type:ignore
        return reverse_lazy(
            "ops:weekly_program_updates_update", kwargs={"pk": weekly_comment.weekly_update.pk}
        )


class WeeklyProgramUpdatesCommentUpdateView(
    WeeklyProgramUpdateCommentsContextMixin, UpdateView, BaseFormMixin
):
    form_class = WeeklyProgramUpdateCommentForm
    model = WeeklyProgramUpdateComment

    def get_success_url(self):
        weekly_comment: WeeklyProgramUpdateComment = self.object  # type:ignore
        return reverse_lazy(
            "ops:weekly_program_updates_update", kwargs={"pk": weekly_comment.weekly_update.pk}
        )


class WeeklyProgramUpdatesCommentDeleteView(
    WeeklyProgramUpdateCommentsContextMixin, DeleteView, BaseFormMixin
):

    form_class = WeeklyProgramUpdateCommentForm
    model = WeeklyProgramUpdateComment
    success_url = reverse_lazy("ops:weekly_program_updates")

    def get_success_url(self) -> str:
        weekly_comment: WeeklyProgramUpdateComment = self.object  # type:ignore
        return reverse_lazy(
            "ops:weekly_program_updates_update", kwargs={"pk": weekly_comment.weekly_update.pk}
        )


class WeeklyProgramUpdateCommentsViewSet(BaseView):
    queryset = WeeklyProgramUpdateComment.objects.filter(
        active=True,
    )
    filterset_class = WeeklyProgramUpdateCommentsFilter
    serializer_class = WeeklyProgramUpdateCommentsReadSerializer
    search_fields = (
        "weekly_update",
        "comment",
    )


class CommodityContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # type: ignore
        context["active"] = "inventory-nav"  # id of active nav element
        context["available_fields_url"] = reverse_lazy("api:commodity-get-available-fields")
        context["dump_data_url"] = reverse_lazy("api:commodity-dump-data")
        context["get_filter_form_url"] = reverse_lazy("api:commodity-get-filter-form")
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
    queryset = Commodity.objects.active()
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


class UoMContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # type: ignore
        context["active"] = "inventory-nav"  # id of active nav element
        context["available_fields_url"] = reverse_lazy("api:uom-get-available-fields")
        context["dump_data_url"] = reverse_lazy("api:uom-dump-data")
        context["get_filter_form_url"] = reverse_lazy("api:uom-get-filter-form")
        context["selected"] = "uoms"  # id of selected page
        return context


class UoMListView(UoMContextMixin, LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/ops/uoms.html"
    permission_required = ("ops.view_uom",)


class UoMCreateView(UoMContextMixin, BaseFormMixin, CreateView):
    form_class = UoMForm
    model = UoM
    success_url = reverse_lazy("ops:uoms")


class UoMUpdateView(UoMContextMixin, BaseFormMixin, UpdateView):
    form_class = UoMForm
    model = UoM
    success_url = reverse_lazy("ops:uoms")


class UoMDeleteView(UoMContextMixin, BaseFormMixin, DeleteView):
    form_class = UoMForm
    model = UoM
    success_url = reverse_lazy("ops:uoms")


class UoMViewSet(BaseView):
    queryset = UoM.objects.active()
    serializer_class = UoMSerializer
    filterset_class = UoMFilter
    ordering_fields = ("name",)
    serializer_fields = ("name",)


class UoMCategoryContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # type: ignore
        context["active"] = "inventory-nav"  # id of active nav element
        context["selected"] = "uom_categories"  # id of selected page
        return context


class UoMCategoryListView(
    UoMCategoryContextMixin, LoginRequiredMixin, ApprovedMixin, TemplateView
):
    template_name = "pages/ops/uom_categories.html"
    permission_required = ("ops.view_uomcategory",)


class UoMCategoryCreateView(UoMCategoryContextMixin, BaseFormMixin, CreateView):
    form_class = UoMCategoryForm
    model = UoMCategory
    success_url = reverse_lazy("ops:uom_categories")


class UoMCategoryUpdateView(UoMCategoryContextMixin, BaseFormMixin, UpdateView):
    form_class = UoMCategoryForm
    model = UoMCategory
    success_url = reverse_lazy("ops:uom_categories")


class UoMCategoryDeleteView(UoMCategoryContextMixin, BaseFormMixin, DeleteView):
    form_class = UoMCategoryForm
    model = UoMCategory
    success_url = reverse_lazy("ops:uom_categories")


class UoMCategoryViewSet(BaseView):
    queryset = UoMCategory.objects.active()
    serializer_class = UoMCategorySerializer
    filterset_class = UoMCategoryFilter
    ordering_fields = ("name", "measure_type")
    serializer_fields = ("name", "measure_type")


class NetworkStatusMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # type: ignore
        context["active"] = "hardware-network-nav"  # id of active nav element
        context["selected"] = "facility_network_status"  # id of selected page
        return context


class FacilityNetworkStatusListView(
    NetworkStatusMixin, LoginRequiredMixin, ApprovedMixin, TemplateView
):
    template_name = "pages/ops/facility_network_status.html"
    permission_required = "ops.view_facilitynetworkstatus"


class FacilityNetworkStatusCreateView(
    NetworkStatusMixin, BaseFormMixin, FormContextMixin, CreateView
):
    form_class = FacilityNetworkStatusForm
    model = FacilityNetworkStatus
    success_url = reverse_lazy("ops:facility_network_status")


class FacilityNetworkStatusUpdateView(
    NetworkStatusMixin, BaseFormMixin, FormContextMixin, UpdateView
):
    form_class = FacilityNetworkStatusForm
    model = FacilityNetworkStatus
    success_url = reverse_lazy("ops:facility_network_status")


class FacilityNetworkStatusDeleteView(NetworkStatusMixin, BaseFormMixin, FormMixin, DeleteView):
    form_class = FacilityNetworkStatusForm
    model = FacilityNetworkStatus
    success_url = reverse_lazy("ops:facility_network_status")


class FacilityNetworkStatusViewSet(BaseView):
    queryset = FacilityNetworkStatus.objects.active()
    serializer_class = FacilityNetworkStatusSerializer
    filterset_class = FacilityNetworkStatusFilter
    ordering_fields = (
        "facility__name",
        "has_network",
        "has_internet",
    )
    search_fields = (
        "facility__name",
        "has_network",
        "has_internet",
    )
    facility_field_lookup = "facility"


class FacilityDevicesMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # type: ignore
        context["active"] = "hardware-network-nav"  # id of active nav element
        context["selected"] = "facility_devices"  # id of selected page
        return context


class FacilityDevicesListView(
    FacilityDevicesMixin, LoginRequiredMixin, ApprovedMixin, TemplateView
):
    template_name = "pages/ops/facility_devices.html"
    permission_required = "ops.view_facilitydevice"


class FacilityDeviceCreateView(FacilityDevicesMixin, BaseFormMixin, FormContextMixin, CreateView):
    form_class = FacilityDeviceForm
    model = FacilityDevice
    success_url = reverse_lazy("ops:facility_devices")


class FacilityDeviceUpdateView(FacilityDevicesMixin, BaseFormMixin, FormContextMixin, UpdateView):
    form_class = FacilityDeviceForm
    model = FacilityDevice
    success_url = reverse_lazy("ops:facility_devices")


class FacilityDeviceDeleteView(FacilityDevicesMixin, BaseFormMixin, FormContextMixin, DeleteView):
    form_class = FacilityDeviceForm
    model = FacilityDevice
    success_url = reverse_lazy("ops:facility_devices")


class FacilityDeviceViewSet(BaseView):
    queryset = FacilityDevice.objects.active()
    serializer_class = FacilityDeviceSerializer
    filterset_class = FacilityDeviceFilter
    ordering_fields = (
        "facility__name",
        "number_of_devices",
        "number_of_ups",
        "server_specification",
    )
    search_fields = (
        "facility__name",
        "number_of_devices",
        "number_of_ups",
    )
    facility_field_lookup = "facility"


class FacilityDeviceRequestsMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # type: ignore
        context["active"] = "hardware-network-nav"  # id of active nav element
        context["selected"] = "facility_device_requests"  # id of selected page
        return context


class FacilityDeviceRequestsListView(
    FacilityDeviceRequestsMixin, LoginRequiredMixin, ApprovedMixin, TemplateView
):
    template_name = "pages/ops/facility_device_requests.html"
    permission_required = "ops.view_facilitydevicerequest"


class FacilityDeviceRequestCreateView(
    FacilityDeviceRequestsMixin, BaseFormMixin, FormContextMixin, CreateView
):
    form_class = FacilityDeviceRequestForm
    model = FacilityDeviceRequest
    success_url = reverse_lazy("ops:facility_device_requests")


class FacilityDeviceRequestUpdateView(
    FacilityDeviceRequestsMixin, BaseFormMixin, FormContextMixin, UpdateView
):
    form_class = FacilityDeviceRequestForm
    model = FacilityDeviceRequest
    success_url = reverse_lazy("ops:facility_device_requests")


class FacilityDeviceRequestDeleteView(
    FacilityDeviceRequestsMixin, BaseFormMixin, FormContextMixin, DeleteView
):
    form_class = FacilityDeviceRequestForm
    model = FacilityDeviceRequest
    success_url = reverse_lazy("ops:facility_device_requests")


class FacilityDeviceRequestViewSet(BaseView):
    queryset = FacilityDeviceRequest.objects.active()
    serializer_class = FacilityDeviceRequestSerializer
    filterset_class = FacilityDeviceRequestFilter
    ordering_fields = (
        "facility__name",
        "device_requested",
        "request_type",
        "request_details",
        "date_requested",
        "delivery_date",
    )
    search_fields = (
        "facility__name",
        "device_requested",
        "request_type",
        "date_requested",
        "delivery_date",
    )
    facility_field_lookup = "facility"


class SecurityIncidenceMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # type: ignore
        context["active"] = "hardware-network-nav"  # id of active nav element
        context["selected"] = "security_incidents"  # id of selected page
        return context


class SecurityIncidentsListView(
    SecurityIncidenceMixin, LoginRequiredMixin, ApprovedMixin, TemplateView
):
    template_name = "pages/ops/security_incidents.html"
    permission_required = "ops.view_securityincidence"


class SecurityIncidenceCreateView(
    SecurityIncidenceMixin, BaseFormMixin, FormContextMixin, CreateView
):
    form_class = SecurityIncidenceForm
    model = SecurityIncidence
    success_url = reverse_lazy("ops:security_incidents")


class SecurityIncidenceUpdateView(
    SecurityIncidenceMixin, BaseFormMixin, FormContextMixin, UpdateView
):
    form_class = SecurityIncidenceForm
    model = SecurityIncidence
    success_url = reverse_lazy("ops:security_incidents")


class SecurityIncidenceDeleteView(
    SecurityIncidenceMixin, BaseFormMixin, FormContextMixin, DeleteView
):
    form_class = SecurityIncidenceForm
    model = SecurityIncidence
    success_url = reverse_lazy("ops:security_incidents")


class SecurityIncidenceViewSet(BaseView):
    queryset = SecurityIncidence.objects.active()
    serializer_class = SecurityIncidenceSerializer
    filterset_class = SecurityIncidenceFilter
    ordering_fields = (
        "facility__name",
        "title",
        "details",
        "reported_on",
        "reported_by",
    )
    search_fields = (
        "facility__name",
        "title",
        "reported_on",
        "reported_by",
    )
    facility_field_lookup = "facility"


class QuestionContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # type: ignore
        context["active"] = "mentorship-nav"  # id of active nav element
        context["selected"] = "questions"  # id of selected page
        return context


class QuestionListView(QuestionContextMixin, LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/ops/questions.html"
    permission_required = "ops.view_question"


class QuestionCreateView(QuestionContextMixin, BaseFormMixin, FormContextMixin, CreateView):
    form_class = QuestionForm
    model = Question
    success_url = reverse_lazy("ops:questions")


class QuestionUpdateView(QuestionContextMixin, BaseFormMixin, FormContextMixin, UpdateView):
    form_class = QuestionForm
    model = Question
    success_url = reverse_lazy("ops:questions")


class QuestionDeleteView(QuestionContextMixin, BaseFormMixin, FormContextMixin, DeleteView):
    form_class = QuestionForm
    model = Question
    success_url = reverse_lazy("ops:questions")


class QuestionViewSet(BaseView):
    queryset = Question.objects.active()
    serializer_class = QuestionSerializer
    filterset_class = QuestionFilter
    ordering_fields = (
        "question",
        "-question_number",
        "-precedence",
    )
    search_fields = ("question",)


class QuestionGroupContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # type: ignore
        context["active"] = "mentorship-nav"  # id of active nav element
        context["selected"] = "question_group"  # id of selected page
        return context


class QuestionGroupListView(
    QuestionGroupContextMixin, LoginRequiredMixin, ApprovedMixin, TemplateView
):
    template_name = "pages/ops/question_groups.html"
    permission_required = "ops.view_question_group"


class QuestionGroupCreateView(
    QuestionGroupContextMixin, BaseFormMixin, FormContextMixin, CreateView
):
    form_class = QuestionGroupForm
    model = QuestionGroup
    success_url = reverse_lazy("ops:question_groups")


class QuestionGroupUpdateView(
    QuestionGroupContextMixin, BaseFormMixin, FormContextMixin, UpdateView
):
    form_class = QuestionGroupForm
    model = QuestionGroup
    success_url = reverse_lazy("ops:question_groups")


class QuestionGroupDeleteView(
    QuestionGroupContextMixin, BaseFormMixin, FormContextMixin, DeleteView
):
    form_class = QuestionGroupForm
    model = QuestionGroup
    success_url = reverse_lazy("ops:question_groups")


class QuestionGroupViewSet(BaseView):
    queryset = QuestionGroup.objects.active()
    serializer_class = QuestionGroupSerializer
    filterset_class = QuestionGroupFilter
    ordering_fields = (
        "title",
        "questions",
        "precedence",
    )
    search_fields = (
        "title",
        "questions",
        "precedence",
    )


class QuestionnaireContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # type: ignore
        context["active"] = "mentorship-nav"  # id of active nav element
        context["selected"] = "questionnaire"  # id of selected page
        return context


class QuestionnaireListView(
    QuestionnaireContextMixin, LoginRequiredMixin, ApprovedMixin, TemplateView
):
    template_name = "pages/ops/questionnaire.html"
    permission_required = "ops.view_questionnaire"


class QuestionnaireCreateView(
    QuestionnaireContextMixin, BaseFormMixin, FormContextMixin, CreateView
):
    form_class = QuestionnaireForm
    model = Questionnaire
    success_url = reverse_lazy("ops:questionnaire")


class QuestionnaireUpdateView(
    QuestionnaireContextMixin, BaseFormMixin, FormContextMixin, UpdateView
):
    form_class = QuestionnaireForm
    model = Questionnaire
    success_url = reverse_lazy("ops:questionnaire")


class QuestionnaireDeleteView(
    QuestionnaireContextMixin, BaseFormMixin, FormContextMixin, DeleteView
):
    form_class = QuestionnaireForm
    model = Questionnaire
    success_url = reverse_lazy("ops:questionnaire")


class QuestionnaireViewSet(BaseView):
    queryset = Questionnaire.objects.active()
    serializer_class = QuestionnaireSerializer
    filterset_class = QuestionnaireFilter
    ordering_fields = (
        "title",
        "question_groups" "-precedence",
    )
    search_fields = ("title",)


# Dynamic MentorshipQuestionnaireViewSet here;
# Should also handle CRUD for QuestionAnswer model
