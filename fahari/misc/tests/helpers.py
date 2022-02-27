import json
from typing import Any, Sequence


def load_google_sheet_test_data() -> Sequence[Any]:
    with open("fahari/misc/tests/resources/google_sheet_test_data.json") as f:
        return json.load(f)
