from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.forms.widgets import DateInput, DateTimeInput, HiddenInput, Select, Textarea, TextInput

from fahari.common.forms import BaseModelForm, GetAllottedFacilitiesMixin
from fahari.common.widgets import SearchableComboBox

from .models import (
    ActivityLog,
    Commodity,
    DailyUpdate,
    FacilityDevice,
    FacilityDeviceRequest,
    FacilityNetworkStatus,
    FacilitySystem,
    FacilitySystemTicket,
    SecurityIncidence,
    SiteMentorship,
    StockReceiptVerification,
    TimeSheet,
    UoM,
    UoMCategory,
    WeeklyProgramUpdate,
    WeeklyProgramUpdateComment,
)


class FacilitySystemForm(GetAllottedFacilitiesMixin, BaseModelForm):
    field_order = (
        "facility",
        "system",
        "version",
        "active",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = "facility_system_form"
        self.fields["facility"].queryset = self.get_allotted_facilities().active()

    class Meta(BaseModelForm.Meta):
        model = FacilitySystem
        widgets = {
            "facility": SearchableComboBox(),
        }


class FacilitySystemTicketForm(GetAllottedFacilitiesMixin, BaseModelForm):

    field_order = (
        "facility_system",
        "details",
        "raised_by",
        "raised",
        "resolved_by",
        "resolved",
        "active",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = "facility_system_ticket_form"
        self.fields["facility_system"].queryset = FacilitySystem.objects.active().filter(
            facility__in=self.get_allotted_facilities()
        )

    class Meta(BaseModelForm.Meta):
        model = FacilitySystemTicket
        widgets = {
            "facility_system": SearchableComboBox(),
            "raised": DateTimeInput(
                attrs={
                    "readonly": "readonly",
                }
            ),
            "raised_by": TextInput(
                attrs={
                    "required": True,
                    "size": 128,
                }
            ),
            "resolved_by": TextInput(
                attrs={
                    "disabled": True,
                    "size": 128,
                }
            ),
            "resolved": DateTimeInput(
                attrs={
                    "readonly": "readonly",
                    "disabled": True,
                }
            ),
            "resolve_note": Textarea(
                attrs={
                    "disabled": True,
                }
            ),
        }


class FacilitySystemTicketResolveForm(forms.Form):
    resolve_note = forms.CharField(
        label="Resolve Comments/Notes", required=False, widget=forms.Textarea
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "post"
        self.helper.form_action = ""
        self.helper.add_input(Submit("submit", "Resolve"))
        self.helper.html5_required = True
        self.helper.form_id = "facility_system_ticket_resolve_form"


class StockReceiptVerificationForm(GetAllottedFacilitiesMixin, BaseModelForm):
    field_order = (
        "facility",
        "commodity",
        "description",
        "pack_size",
        "delivery_note_number",
        "quantity_received",
        "batch_number",
        "delivery_date",
        "expiry_date",
        "delivery_note_image",
        "comments",
        "active",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = "stock_receipt_verification_form"
        self.fields["facility"].queryset = self.get_allotted_facilities().active()
        self.fields["delivery_note_image"].required = True

    class Meta(BaseModelForm.Meta):
        model = StockReceiptVerification
        widgets = {
            "facility": SearchableComboBox(),
            "commodity": SearchableComboBox(),
            "delivery_date": TextInput(attrs={"type": "date"}),
            "expiry_date": TextInput(attrs={"type": "date"}),
        }


class ActivityLogForm(BaseModelForm):
    field_order = (
        "activity",
        "planned_date",
        "requested_date",
        "procurement_date",
        "finance_approval_date",
        "final_approval_date",
        "done_date",
        "invoiced_date",
        "remarks",
        "active",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = "activity_log_form"

    class Meta(BaseModelForm.Meta):
        model = ActivityLog
        widgets = {
            "planned_date": TextInput(
                attrs={
                    "type": "date",
                }
            ),
            "requested_date": TextInput(
                attrs={
                    "type": "date",
                }
            ),
            "procurement_date": TextInput(
                attrs={
                    "type": "date",
                }
            ),
            "finance_approval_date": TextInput(
                attrs={
                    "type": "date",
                }
            ),
            "final_approval_date": TextInput(
                attrs={
                    "type": "date",
                }
            ),
            "done_date": TextInput(
                attrs={
                    "type": "date",
                }
            ),
            "invoiced_date": TextInput(
                attrs={
                    "type": "date",
                }
            ),
        }


class SiteMentorshipForm(GetAllottedFacilitiesMixin, BaseModelForm):
    field_order = (
        "staff_member",
        "site",
        "day",
        "duration",
        "objective",
        "pick_up_point",
        "drop_off_point",
        "active",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = "site_mentorship_form"
        self.fields["site"].queryset = self.get_allotted_facilities().active()

    class Meta(BaseModelForm.Meta):
        model = SiteMentorship
        widgets = {
            "day": TextInput(
                attrs={
                    "type": "date",
                }
            ),
            "site": SearchableComboBox(),
        }


class DailyUpdateForm(GetAllottedFacilitiesMixin, BaseModelForm):
    field_order = (
        "facility",
        "date",
        "total",
        "clients_booked",
        "kept_appointment",
        "missed_appointment",
        "came_early",
        "unscheduled",
        "new_ft",
        "ipt_new_adults",
        "ipt_new_paeds",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = "daily_update_form"
        self.fields["facility"].queryset = self.get_allotted_facilities().active()

    class Meta(BaseModelForm.Meta):
        model = DailyUpdate
        widgets = {
            "facility": SearchableComboBox(),
            "date": TextInput(
                attrs={
                    "type": "date",
                }
            ),
        }


class TimeSheetForm(BaseModelForm):
    field_order = (
        "date",
        "activity",
        "output",
        "hours",
        "location",
        "staff",
        "approved_by",
        "approved_at",
        "active",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = "time_sheet_form"

    class Meta(BaseModelForm.Meta):
        model = TimeSheet
        widgets = {
            "date": TextInput(
                attrs={
                    "type": "date",
                }
            ),
            "approved_at": TextInput(
                attrs={
                    "type": "datetime-local",
                    "readonly": "readonly",
                    "disabled": "disabled",
                }
            ),
            "approved_by": Select(
                attrs={
                    "readonly": "readonly",
                    "disabled": "disabled",
                }
            ),
        }


class WeeklyProgramUpdateForm(BaseModelForm):
    field_order = (
        "facility",
        "operation_area",
        "date_created",
        "status",
        "assigned_persons",
        "active",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = "weekly_program_update_form"
        self.fields["date_created"].widget = HiddenInput()

    class Meta(BaseModelForm.Meta):
        model = WeeklyProgramUpdate
        widgets = {
            "facility": SearchableComboBox(),
        }

    class Media:
        js = ("js/weekly_program_update_form.min.js",)


class WeeklyProgramUpdateCommentForm(BaseModelForm):
    field_order = (
        "weekly_update",
        "comment",
        "active",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = "weekly_program_update_comment_form"
        self.fields["weekly_update"].widget = HiddenInput()
        self.fields["date_created"].widget = HiddenInput()
        self.fields["active"].widget = HiddenInput()

    class Meta(BaseModelForm.Meta):
        model = WeeklyProgramUpdateComment


class CommodityForm(BaseModelForm):

    field_order = [
        "name",
        "code",
        "pack_sizes",
        "description",
        "is_lab_commodity",
        "is_pharmacy_commodity",
        "active",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = "commodity_form"

    class Meta(BaseModelForm.Meta):
        model = Commodity


class UoMForm(BaseModelForm):

    field_order = ("name", "category", "active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = "uom_form"

    class Meta(BaseModelForm.Meta):
        model = UoM


class UoMCategoryForm(BaseModelForm):

    field_order = ("name", "measure_type", "active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = "uom_category_form"

    class Meta(BaseModelForm.Meta):
        model = UoMCategory


class FacilityNetworkStatusForm(GetAllottedFacilitiesMixin, BaseModelForm):
    field_order = (
        "facility",
        "has_network",
        "has_internet",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = "facility_network_status_form"
        self.fields["facility"].queryset = self.get_allotted_facilities().active()

    class Meta(BaseModelForm.Meta):
        model = FacilityNetworkStatus
        widgets = {
            "facility": SearchableComboBox(),
        }


class FacilityDeviceForm(GetAllottedFacilitiesMixin, BaseModelForm):
    field_order = (
        "facility",
        "number_of_devices",
        "number_of_ups",
        "server_specification",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = "facility_device_form"
        self.fields["facility"].queryset = self.get_allotted_facilities().active()

    class Meta(BaseModelForm.Meta):
        model = FacilityDevice
        widgets = {
            "facility": SearchableComboBox(),
        }


class FacilityDeviceRequestForm(GetAllottedFacilitiesMixin, BaseModelForm):
    field_order = (
        "facility",
        "device_requested",
        "request_type",
        "request_details",
        "date_requested",
        "delivery_date",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = "facility_device_request_form"
        self.fields["facility"].queryset = self.get_allotted_facilities().active()

    class Meta(BaseModelForm.Meta):
        model = FacilityDeviceRequest
        widgets = {
            "facility": SearchableComboBox(),
            "date_requested": DateInput(attrs={"hidden": True}),
            "delivery_date": DateInput(
                attrs={
                    "hidden": True,
                }
            ),
        }


class SecurityIncidenceForm(GetAllottedFacilitiesMixin, BaseModelForm):
    field_order = (
        "facility",
        "title",
        "details",
        "reported_on",
        "reported_by",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = "security_incidence_form"
        self.fields["facility"].queryset = self.get_allotted_facilities().active()

    class Meta(BaseModelForm.Meta):
        model = SecurityIncidence
        widgets = {
            "facility": SearchableComboBox(),
            "reported_on": DateInput(attrs={"hidden": True}),
        }
