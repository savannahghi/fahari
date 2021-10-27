from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Fieldset, Layout
from django import forms

from .models import StockVerificationReceiptsAdapter


class ImportStockVerificationReceiptsForm(forms.Form):
    """A form for selecting the stock verification adapter to use."""

    adapter = forms.ModelChoiceField(queryset=StockVerificationReceiptsAdapter.objects.active())
    status = forms.CharField(disabled=True, required=False, widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["adapter"].label = "County"
        self.helper = FormHelper(self)
        self.helper.form_class = "form-horizontal"
        self.helper.form_method = "post"
        self.helper.form_action = ""
        self.helper.html5_required = True
        self.helper.form_id = "import_stock_verification_receipts_form"
        self.helper.label_class = "col-lg-2"
        self.helper.field_class = "col-lg-8"
        self.helper.layout = Layout(
            "adapter",
            Fieldset(
                "",
                Field("status", style="font-family:monospace;font-size: 13px;"),
                css_id="status_fieldset",
            ),
        )

    class Media:
        js = ("js/import_stock_verification_receipts_form.min.js",)
