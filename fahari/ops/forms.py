from django.forms.widgets import DateTimeInput, TextInput

from fahari.common.constants import WHITELIST_COUNTIES
from fahari.common.forms import BaseModelForm
from fahari.common.models import Facility

from .models import FacilitySystem, FacilitySystemTicket


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
        self.fields["facility"].queryset = Facility.objects.filter(
            is_fahari_facility=True,
            operation_status="Operational",
            county__in=WHITELIST_COUNTIES,
            active=True,
        )

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
