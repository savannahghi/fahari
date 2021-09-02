"""
Custom widgets to supplement/replace existing widgets.
"""
from django import forms


class SearchableComboBox(forms.Select):
    """A combo box with search capabilities.

    This is suitable as a replacement for select with many options.
    """

    input_type = "select"
    option_inherits_attrs = False

    def build_attrs(self, base_attrs, extra_attrs=None):
        # The `data-live-search` attribute is needed to enable the search
        # functionality.
        base_attrs.update({"data-live-search": "true"})
        return super().build_attrs(base_attrs, extra_attrs)
