from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.forms import ModelForm, TextInput

from .models import Facility, FacilityAttachment, Organisation, System


class BaseModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "post"
        self.helper.form_action = ""
        self.helper.add_input(Submit("submit", "Save"))
        self.helper.html5_required = True

    class Meta:
        exclude = (
            "created",
            "updated",
            "created_by",
            "updated_by",
            "organisation",
        )


class FacilityForm(BaseModelForm):
    field_order = (
        "name",
        "mfl_code",
        "active",
        "is_fahari_facility",
        "county",
        "sub_county",
        "constituency",
        "ward",
        "lon",
        "lat",
        "operation_status",
        "registration_number",
        # others as defined on the model
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = "facility_form"

    class Meta:
        model = Facility
        widgets = {
            "name": TextInput(
                attrs={
                    "required": True,
                    "size": 64,
                }
            ),
        }
        exclude = (
            "created",
            "updated",
            "created_by",
            "updated_by",
            "organisation",
            "public_visible",
            "approved",
            "closed",
            "open_late_night",
            "open_weekends",
            "open_public_holidays",
            "open_whole_day",
            "beds",
            "cots",
            "facility_owner",
            "regulatory_body",
        )


class SystemForm(BaseModelForm):
    field_order = (
        "name",
        "description",
        "active",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = "system_form"

    class Meta(BaseModelForm.Meta):
        model = System


class OrganisationForm(BaseModelForm):
    class Meta:
        model = Organisation
        fields = "__all__"


class FacilityAttachmentForm(BaseModelForm):
    class Meta:
        model = FacilityAttachment
        fields = "__all__"
