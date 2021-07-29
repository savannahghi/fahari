from django.forms.widgets import DateTimeInput, TextInput

from fahari.common.dashboard import get_fahari_facilities_queryset
from fahari.common.forms import BaseModelForm

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


class FacilitySystemForm(BaseModelForm):
    field_order = (
        "facility",
        "system",
        "version",
        "active",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = "facility_system_form"
        self.fields["facility"].queryset = get_fahari_facilities_queryset()

    class Meta(BaseModelForm.Meta):
        model = FacilitySystem


class FacilitySystemTicketForm(BaseModelForm):

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

    class Meta(BaseModelForm.Meta):
        model = FacilitySystemTicket
        widgets = {
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
                    "disabled": True,
                }
            ),
        }


class StockReceiptVerificationForm(BaseModelForm):
    field_order = (
        "facility",
        "description",
        "pack_size",
        "delivery_note_number",
        "quantity_received",
        "batch_number",
        "expiry_date",
        "comments",
        "active",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = "stock_receipt_verification_form"
        self.fields["facility"].queryset = get_fahari_facilities_queryset()

    class Meta(BaseModelForm.Meta):
        model = StockReceiptVerification
        widgets = {
            "pack_size": TextInput(
                attrs={
                    "size": 128,
                }
            ),
            "expiry_date": TextInput(
                attrs={
                    "type": "date",
                }
            ),
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


class SiteMentorshipForm(BaseModelForm):
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
        self.fields["site"].queryset = get_fahari_facilities_queryset()

    class Meta(BaseModelForm.Meta):
        model = SiteMentorship
        widgets = {
            "day": TextInput(
                attrs={
                    "type": "date",
                }
            ),
        }


class DailyUpdateForm(BaseModelForm):
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
        self.fields["facility"].queryset = get_fahari_facilities_queryset()

    class Meta(BaseModelForm.Meta):
        model = DailyUpdate
        widgets = {
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
                }
            ),
        }


class WeeklyProgramUpdateForm(BaseModelForm):
    field_order = (
        "date",
        "attendees",
        "active",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = "weekly_program_update_form"

    class Meta(BaseModelForm.Meta):
        model = WeeklyProgramUpdate
