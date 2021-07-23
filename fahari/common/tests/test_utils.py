"""Define utilities used in test."""
from functools import partial
from unittest.mock import patch

from model_bakery import baker


def compare_dict(dict1, dict2):
    """Compare two dictionaries.

    This function checks that two objects that contain similar keys
    have the same value

    """
    dict1_keys = set(dict1)
    dict2_keys = set(dict2)
    intersect = dict1_keys.intersection(dict2_keys)

    if not intersect:
        return False

    for key in intersect:
        if dict1[key] != dict2[key]:
            return False
    return True


def mock_baker(values):
    """Create test fixture."""
    assert isinstance(values, dict), (
        "Expects " "{field_name, field_value} dict. " f"Found {type(values)}"
    )

    class _Baker(baker.Baker):

        fields = values

        def _get_field_names(self):
            return [each.name for each in self.get_fields()]

        def _make(self, *args, **attrs):
            for field_name, value in self.fields.items():
                if field_name in self._get_field_names():
                    attrs.setdefault(field_name, value)
            return super()._make(*args, **attrs)

    return _Baker


patch_baker = partial(patch, "model_bakery.baker.Baker", new_callable=mock_baker)


def make_transitions(obj, transitions, note={}):
    """Change state of organisation."""
    for each in transitions:
        obj.workflow_state = each
        obj.transition(note)
    return obj
