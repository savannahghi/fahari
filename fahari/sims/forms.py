from crispy_forms.helper import FormHelper
from django import forms

from fahari.common.forms import BaseModelForm, GetAllottedFacilitiesMixin
from fahari.common.widgets import SearchableComboBox

from .models import QuestionnaireResponses


class MentorshipTeamMemberForm(forms.Form):
    name = forms.CharField(max_length=255, min_length=3)
    role = forms.CharField(max_length=255, min_length=2)
    member_org = forms.CharField(max_length=255, min_length=2, label="Organisation")
    phone_number = forms.CharField(max_length=255, min_length=3)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.disable_csrf = True
        self.helper.form_action = ""
        self.helper.form_id = "mentorship_details_form"
        self.helper.form_method = "post"
        self.helper.html5_required = True


class QuestionnaireResponsesForm(GetAllottedFacilitiesMixin, forms.ModelForm):
    field_order = ("questionnaire" "facility",)

    mentors = forms.JSONField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = ""
        self.helper.form_id = "questionnaire_response_form"
        self.helper.form_method = "post"
        self.helper.html5_required = True
        self.fields["questionnaire"].disabled = True
        self.fields["facility"].queryset = self.get_allotted_facilities().active()

    class Meta(BaseModelForm.Meta):
        fields = "facility", "questionnaire", "mentors"
        model = QuestionnaireResponses
        widgets = {"facility": SearchableComboBox()}
