#!/usr/bin/env python
import os
import sys
from pathlib import Path

import django
import pyexcel
from django.core.exceptions import ValidationError

MFL_CODE_COLNAME = "MFL CODE"
MFL_SHEET_NAME = "fyj_sites"


def mark_facilities(source_path):
    from fahari.common.models import Facility

    records = pyexcel.get_records(file_name=source_path, sheet_name=MFL_SHEET_NAME)
    count = len(records)
    for pos, r in enumerate(records):
        code = r[MFL_CODE_COLNAME]
        if code is not None and code != "None" and code != "":
            try:
                facility = Facility.objects.get(mfl_code=r[MFL_CODE_COLNAME])
                facility.is_fahari_facility = True
                facility.save()
                print(f"Facility: {facility} marked as a Fahari facility; Pos {pos + 1}/{count}")
            except Facility.DoesNotExist:
                print(f"no facility with code {r[MFL_CODE_COLNAME]}")
            except ValidationError as e:
                print(f"can't save row {r}, got error {e}")


if __name__ == "__main__":
    base_path = Path(__file__).parent.parent.resolve()
    print(base_path)
    sys.path.append(str(base_path))
    sys.path.append(str(base_path / "fahari"))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
    django.setup()

    data_dir = os.path.join(base_path, "data")
    source_file = os.path.join(data_dir, "updated_fyj_sites.xlsx")
    mark_facilities(source_file)
