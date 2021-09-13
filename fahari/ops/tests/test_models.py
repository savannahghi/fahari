import random
from datetime import date

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from faker import Faker
from model_bakery import baker

from fahari.common.models import Facility, Organisation, System
from fahari.common.tests.test_api import global_organisation
from fahari.ops.models import (
    DEFAULT_COMMODITY_PK,
    Activity,
    ActivityLog,
    Commodity,
    DailyUpdate,
    FacilityDevice,
    FacilityDeviceRequest,
    FacilityNetworkStatus,
    FacilitySystem,
    FacilitySystemTicket,
    OperationalArea,
    SecurityIncidence,
    SiteMentorship,
    StockReceiptVerification,
    TimeSheet,
    UoM,
    UoMCategory,
    WeeklyProgramUpdate,
    default_commodity,
    default_end_time,
    default_start_time,
)

pytestmark = pytest.mark.django_db

fake = Faker()


def test_facility_system_str():
    org = baker.make(Organisation)
    facility = baker.make(Facility, organisation=org, name="Test")
    system = baker.make(System, organisation=org, name="System")
    vrs = "0.0.1"
    facility_system = baker.make(
        FacilitySystem,
        facility=facility,
        system=system,
        version=vrs,
    )
    assert str(facility_system) == "Test - System, version 0.0.1"


def test_facility_system_ticket_str():
    org = baker.make(Organisation)
    facility = baker.make(Facility, organisation=org, name="Test")
    system = baker.make(System, organisation=org, name="System")
    vrs = "0.0.1"
    facility_system = baker.make(
        FacilitySystem,
        facility=facility,
        system=system,
        version=vrs,
    )
    facility_system_details = baker.make(
        FacilitySystemTicket,
        facility_system=facility_system,
        details="Details",
    )
    assert (
        str(facility_system_details) == "Facility: Test; System: System; Version: 0.0.1 (Details)"
    )


def test_facility_system_ticket_is_resolved():
    org = baker.make(Organisation)
    facility = baker.make(Facility, organisation=org, name="Test")
    system = baker.make(System, organisation=org, name="System")
    vrs = "0.0.1"
    facility_system = baker.make(
        FacilitySystem,
        facility=facility,
        system=system,
        version=vrs,
    )
    facility_system_details = baker.make(
        FacilitySystemTicket,
        facility_system=facility_system,
        details="Details",
        resolved=timezone.now(),
        resolved_by="User",
    )
    assert facility_system_details.is_resolved is True


def test_facility_ticket_status(staff_user):
    open_ticket = baker.make(FacilitySystemTicket, resolved=None, resolved_by=None)
    assert open_ticket.is_open is True

    closed_ticket = baker.make(
        FacilitySystemTicket, resolved=timezone.now(), resolved_by=staff_user
    )
    assert closed_ticket.is_open is False


def get_random_date():
    year = random.randint(1900, 2100)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return date(year=year, month=month, day=day)


def test_timesheet_is_full_day(user, staff_user):
    full_day_timesheet = baker.make(
        TimeSheet,
        hours=9,
        staff=user,
        approved_at=timezone.now(),
        approved_by=staff_user,
        date=get_random_date(),
    )
    assert full_day_timesheet.is_full_day is True

    part_day_timesheet = baker.make(
        TimeSheet,
        hours=7,
        staff=staff_user,
        approved_at=timezone.now(),
        approved_by=staff_user,
        date=get_random_date(),
    )
    assert part_day_timesheet.is_full_day is False


def test_timesheet_is_approved(user, staff_user):
    approved_timesheet = baker.make(
        TimeSheet,
        approved_at=timezone.now(),
        staff=user,
        approved_by=staff_user,
        date=get_random_date(),
    )
    assert approved_timesheet.is_approved is True

    non_approved_timesheet = baker.make(
        TimeSheet,
        approved_at=None,
        staff=user,
        approved_by=None,
        date=get_random_date(),
    )
    assert non_approved_timesheet.is_approved is False


def test_timesheet_validate_approval(user, staff_user):
    with pytest.raises(ValidationError) as e:
        bad_timesheet = baker.prepare(
            TimeSheet, staff=user, approved_at=timezone.now(), approved_by=None
        )
        bad_timesheet.save()

    assert "approved_at and approved_by must both be set" in str(e)

    with pytest.raises(ValidationError) as e:
        bad_timesheet = baker.prepare(
            TimeSheet, approved_at=None, staff=user, approved_by=staff_user
        )
        bad_timesheet.save()

    assert "approved_at and approved_by must both be set" in str(e)


def test_facility_ticket_validate_resolved():
    with pytest.raises(ValidationError) as e:
        bad_ticket_resolve = baker.prepare(
            FacilitySystemTicket, resolved=timezone.now(), resolved_by=None
        )
        bad_ticket_resolve.save()

    assert "resolved and resolved_by must both be set" in str(e)


def test_daily_update_appointment_keeping_percentage():
    update_with_no_clients_booked = baker.make(DailyUpdate, clients_booked=0)
    assert update_with_no_clients_booked.appointment_keeping == 0

    update_with_all_clients_kept = baker.make(DailyUpdate, kept_appointment=5, clients_booked=5)
    assert update_with_all_clients_kept.appointment_keeping == 100

    update_with_half_booking = baker.make(DailyUpdate, kept_appointment=2, clients_booked=4)
    assert update_with_half_booking.appointment_keeping == 50


def test_default_start_time():
    assert default_start_time().hour == 8


def test_default_end_time():
    assert default_end_time().hour == 18


def test_string_reprs():
    # cheat
    models = [
        TimeSheet,
        ActivityLog,
        SiteMentorship,
        DailyUpdate,
        StockReceiptVerification,
        OperationalArea,
        Activity,
        WeeklyProgramUpdate,
    ]
    for model in models:
        instance = baker.prepare(model)
        assert str(instance) != ""


def test_default_commodity():
    first = default_commodity()
    subsequent = default_commodity()

    assert first == subsequent
    assert str(first) == DEFAULT_COMMODITY_PK


def test_commodity_str():
    commodity = baker.make(Commodity, name="Test", code="001")
    assert str(commodity) == "Test (001)"


def test_commodity_url():
    commodity = baker.make(
        Commodity,
        name="Test",
        code="001",
    )
    url = commodity.get_absolute_url()
    assert f"/ops/commodity_update/{commodity.pk}" in url


def test_uom_str():
    uom = baker.make(UoM, name="300 Units")
    assert str(uom) == "300 Units"


def test_uom_url():
    uom = baker.make(UoM, name="Meter")
    url = uom.get_absolute_url()
    assert f"/ops/uom_update/{uom.pk}" in url


def test_uom_category_str():
    uom_category = baker.make(UoMCategory, name="Pack size")
    assert str(uom_category) == "Pack size"


def test_uom_category_url():
    uom_category = baker.make(UoMCategory, name="Pack size")
    url = uom_category.get_absolute_url()
    assert f"/ops/uom_category_update/{uom_category.pk}" in url


def test_stock_receipt_verification_with_valid_pack_size():
    organisation = global_organisation()
    pack_sizes = baker.make(UoM, 4, organisation=organisation)
    commodity = baker.make(Commodity, pack_sizes=pack_sizes, organisation=organisation)
    stock_receipt = baker.make(
        StockReceiptVerification,
        commodity=commodity,
        pack_size=pack_sizes[0],
        organisation=organisation,
    )

    assert stock_receipt is not None
    assert stock_receipt.pack_size in commodity.pack_sizes.all()


def test_stock_receipt_verification_with_invalid_pack_size():
    organisation = global_organisation()
    pack_size = baker.make(UoM, organisation=organisation)
    pack_sizes = baker.make(UoM, 4, organisation=organisation)
    commodity = baker.make(Commodity, pack_sizes=pack_sizes, organisation=organisation)
    with pytest.raises(ValidationError) as e:
        baker.make(
            StockReceiptVerification,
            commodity=commodity,
            pack_size=pack_size,
            organisation=organisation,
        )

    assert (
        '"%s" is not a valid pack size for the commodity "%s"' % (pack_size.name, commodity.name)
        in e.value.messages
    )


def test_facility_network_status_str():
    org = baker.make(Organisation)
    facility = baker.make(Facility, organisation=org, name=fake.text(max_nb_chars=30))
    network_status = baker.make(
        FacilityNetworkStatus,
        facility=facility,
        has_network=fake.pybool(),
        has_internet=fake.pybool(),
    )
    assert str(network_status) == "Facility: %s, Has network: %s, Has internet: %s" % (
        network_status.facility.name,
        network_status.has_network,
        network_status.has_internet,
    )


def test_facility_network_status():
    set_network = baker.make(FacilityNetworkStatus, has_network=True)
    assert set_network.has_network

    set_internet = baker.make(FacilityNetworkStatus, has_internet=False)
    assert not set_internet.has_internet


def test_facility_device_str():
    org = baker.make(Organisation)
    facility = baker.make(Facility, organisation=org, name=fake.text(max_nb_chars=30))
    facility_device = baker.make(
        FacilityDevice,
        facility=facility,
        number_of_devices=random.randint(1, 10),
        number_of_ups=random.randint(1, 10),
        server_specification=fake.text(),
    )
    assert str(facility_device) == "Facility: %s, No.of devices: %s" % (
        facility_device.facility.name,
        facility_device.number_of_devices,
    )


def test_facility_hardware_count():
    device_count = baker.make(FacilityDevice, number_of_devices=random.randint(1, 10))
    assert device_count.number_of_devices >= 1

    ups_count = baker.make(FacilityDevice, number_of_ups=random.randint(1, 10))
    assert ups_count.number_of_ups >= 1


def test_facility_device_request_str():
    org = baker.make(Organisation)
    facility = baker.make(Facility, organisation=org, name=fake.text(max_nb_chars=30))
    facility_device_req = baker.make(
        FacilityDeviceRequest,
        facility=facility,
        device_requested=fake.text(max_nb_chars=50),
        request_type="NEW",
        request_details=fake.text(),
    )
    assert str(facility_device_req) == "Facility: %s, Request type: %s, Device requested: %s" % (
        facility_device_req.facility.name,
        facility_device_req.request_type,
        facility_device_req.device_requested,
    )
    url = facility_device_req.get_absolute_url()
    assert f"/ops/facility_device_request_update/{facility_device_req.pk}" in url


def test_security_incidence_str():
    org = baker.make(Organisation)
    facility = baker.make(Facility, organisation=org, name=fake.text(max_nb_chars=30))
    sec_incidence = baker.make(
        SecurityIncidence,
        facility=facility,
        title=fake.text(max_nb_chars=50),
        details=fake.text(),
    )
    assert str(sec_incidence) == "Facility: %s, Security incidence: %s" % (
        sec_incidence.facility.name,
        sec_incidence.title,
    )
    url = sec_incidence.get_absolute_url()
    assert f"/ops/security_incidence_update/{sec_incidence.pk}" in url
