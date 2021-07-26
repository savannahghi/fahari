from datetime import date
from random import randint

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from faker import Faker
from model_bakery import baker

from fahari.common.models import Facility, Organisation, System
from fahari.ops.models import (
    Activity,
    ActivityLog,
    DailyUpdate,
    FacilitySystem,
    FacilitySystemTicket,
    OperationalArea,
    SiteMentorship,
    StockReceiptVerification,
    TimeSheet,
    WeeklyProgramUpdate,
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


def test_facility_ticket_validate_resolved(staff_user):
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
