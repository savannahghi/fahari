#!/usr/bin/env python
import os
import sys
from pathlib import Path

import django
import requests

URL = (
    "http://api.kmhfl.health.go.ke/api/facilities/material/"
    "?fields=id,code,name,regulatory_status_name,facility_type_name,"
    "owner_name,county,constituency,ward_name,keph_level,operation_status_name?page_size=100"
)
PROJECT_ID = "sghi-307909"
SECRET_NAME = "mfl_authentication_token"
BEARER_TOKEN = "RwYcApURXBLii4PgAsExWMndfujSmo"


def get_long_lat_data():
    """Get data from MFL API."""
    headers = {
        "Authorization": "Bearer {}".format(BEARER_TOKEN),
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    output = []

    first_page = requests.get(URL, headers=headers).json()
    output.extend(first_page["results"])
    num_pages = first_page["total_pages"]

    for page in range(2, num_pages + 1):
        next_page = requests.get(URL, headers=headers, params={"page": page}).json()
        output.extend(next_page["results"])
        print(f"Page {page}/{num_pages}")

    print("Done, starting the updates...")
    update_long_lat(output)


def update_long_lat(data):
    from fahari.common.models import Facility

    count = len(data)
    for idx, row in enumerate(data):
        mfl_code = row["code"]
        if mfl_code is None:
            continue

        lat = row["lat"]
        lon = row["long"]

        try:
            facility = Facility.objects.get(mfl_code=mfl_code)
            facility.lon = lon
            facility.lat = lat
            facility.save()
        except Facility.DoesNotExist:
            print(f"no facility with MFL Code {mfl_code}, please add it")
            continue

        if (idx + 1) % 10 == 0:
            print(f"#{idx+1}/{count}")


if __name__ == "__main__":
    base_path = Path(__file__).parent.parent.resolve()
    print(base_path)
    sys.path.append(str(base_path))
    sys.path.append(str(base_path / "fahari"))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
    django.setup()

    get_long_lat_data()
