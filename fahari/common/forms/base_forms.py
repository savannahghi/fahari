from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.forms import ModelForm

from .mixins import FormContextMixin


class BaseModelForm(FormContextMixin, ModelForm):
    """Base form for the majority of model forms in the project."""

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
