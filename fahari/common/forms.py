from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Fieldset, Layout, Submit
from django.forms import ModelForm, MultipleChoiceField, TextInput

from .dashboard import get_fahari_facilities_queryset
from .models import (
    Facility,
    FacilityAttachment,
    FacilityUser,
    Organisation,
    System,
    UserFacilityAllotment,
)
from .utils import get_constituencies, get_counties, get_sub_counties, get_wards
from .widgets import MultiSearchableComboBox, SearchableComboBox


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
        "pattern",
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
        widgets = {"facility": SearchableComboBox()}


class FacilityUserForm(BaseModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = "facility_user_form"
        self.fields["facility"].queryset = get_fahari_facilities_queryset()

    field_order = (
        "facility",
        "user",
        "active",
    )

    class Meta(BaseModelForm.Meta):
        model = FacilityUser
        fields = "__all__"
        widgets = {"facility": SearchableComboBox()}


class UserFacilityAllotmentForm(BaseModelForm):
    counties = MultipleChoiceField(
        choices=get_counties(),
        help_text=(
            "All the facilities in the selected counties will be allocated to the selected user."
        ),
        required=False,
    )
    constituencies = MultipleChoiceField(
        choices=get_constituencies(),
        help_text=(
            "All the facilities in the selected constituencies will be allocated to the selected "
            "user."
        ),
        required=False,
        widget=MultiSearchableComboBox,
    )
    sub_counties = MultipleChoiceField(
        choices=get_sub_counties(),
        help_text=(
            "All the facilities in the selected sub counties will be allocated to the selected "
            "user."
        ),
        required=False,
        widget=MultiSearchableComboBox,
    )
    wards = MultipleChoiceField(
        choices=get_wards(),
        help_text=(
            "All the facilities in the selected wards will be allocated to the selected user."
        ),
        required=False,
        widget=MultiSearchableComboBox,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["facilities"].queryset = get_fahari_facilities_queryset()
        self.helper.form_id = "user_facility_allotment_form"
        self.helper.layout = Layout(
            Field("user"),
            Field("allotment_type"),
            Fieldset("Allot by Facility", "facilities", css_id="allot_by_facility_fieldset"),
            Fieldset(
                "Allot by Region",
                "region_type",
                "counties",
                "constituencies",
                "sub_counties",
                "wards",
                css_id="allot_by_region_fieldset",
            ),
            Field("active"),
        )

    class Meta(BaseModelForm.Meta):
        model = UserFacilityAllotment
        fields = "__all__"
        widgets = {
            "facilities": MultiSearchableComboBox(),
            "user": SearchableComboBox(),
        }

    class Media:
        js = ("js/user_facility_allotment_form.min.js",)
