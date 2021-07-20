#!/usr/bin/env python
import os
import sys
from pathlib import Path

import django
import pyexcel


def get_created_by_pk():
    from fahari.users.models import User

    return User.objects.filter(is_staff=True)[0].pk


def get_organisation():
    from fahari.common.models import Organisation

    return Organisation.objects.get(code=1)


def load_facilities(source_path):
    from fahari.common.models import Facility

    created_by = get_created_by_pk()
    org = get_organisation()

    records = pyexcel.get_records(file_name=source_path)
    count = len(records)
    for pos, r in enumerate(records):
        if r["Code"] is not None and r["Code"] != "None":
            facility, created = Facility.objects.get_or_create(
                name=r["Name"],
                mfl_code=r["Code"],
                defaults={
                    "created_by": created_by,
                    "updated_by": created_by,
                    "organisation": org,
                    "registration_number": r["Registration_number"],
                    "keph_level": r["Keph level"],
                    "facility_type": r["Facility type"],
                    "facility_type_category": r["Facility_type_category"],
                    "facility_owner": r["Owner"],
                    "owner_type": r["Owner type"],
                    "regulatory_body": r["Regulatory body"],
                    "beds": int(r["Beds"]),
                    "cots": int(r["Cots"]),
                    "county": r["County"],
                    "constituency": r["Constituency"],
                    "sub_county": r["Sub county"],
                    "ward": r["Ward"],
                    "operation_status": r["Operation status"],
                    "open_whole_day": r["Open_whole_day"] == "Yes",
                    "open_public_holidays": r["Open_public_holidays"] == "Yes",
                    "open_weekends": r["Open_weekends"] == "Yes",
                    "open_late_night": r["Open_late_night"] == "Yes",
                    "approved": r["Approved"] == "Yes",
                    "public_visible": r["Public visible"] == "Yes",
                    "closed": r["Closed"] == "Yes",
                },
            )
            print(f"Facility: {facility}; Created: {created}; Pos {pos + 1}/{count}")


if __name__ == "__main__":
    base_path = Path(__file__).parent.parent.resolve()
    print(base_path)
    sys.path.append(str(base_path))
    sys.path.append(str(base_path / "fahari"))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
    django.setup()

    data_dir = os.path.join(base_path, "data")
    source_file = os.path.join(data_dir, "all_mfl_facilities.xlsx")
    load_facilities(source_file)
