from datetime import date
from random import randint

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from faker import Faker
from model_bakery import baker

from fahari.common.models import Facility, Organisation, System
from fahari.ops.models import (
    DEFAULT_COMMODITY_PK,
    Activity,
    ActivityLog,
    Commodity,
    DailyUpdate,
    FacilitySystem,
    FacilitySystemTicket,
    OperationalArea,
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
    year = randint(1900, 2100)
    month = randint(1, 12)
    day = randint(1, 28)
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
