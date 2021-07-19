import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from model_bakery import baker

from pepfar_mle.ops.models import DailyUpdate, FacilitySystemTicket, TimeSheet

pytestmark = pytest.mark.django_db


def test_facility_ticket_status(admin_user):
    open_ticket = baker.make(FacilitySystemTicket, resolved=None, resolved_by=None)
    assert open_ticket.is_open is True

    closed_ticket = baker.make(
        FacilitySystemTicket, resolved=timezone.now(), resolved_by=admin_user
    )
    assert closed_ticket.is_open is False


def test_timesheet_is_full_day():
    full_day_timesheet = baker.make(TimeSheet, hours=9)
    assert full_day_timesheet.is_full_day is True

    part_day_timesheet = baker.make(TimeSheet, hours=7)
    assert part_day_timesheet.is_full_day is False


def test_timesheet_is_approved(admin_user):
    approved_timesheet = baker.make(TimeSheet, approved_at=timezone.now(), approved_by=admin_user)
    assert approved_timesheet.is_approved is True

    non_approved_timesheet = baker.make(TimeSheet, approved_at=None, approved_by=None)
    assert non_approved_timesheet.is_approved is False


def test_timesheet_validate_approval(admin_user):
    with pytest.raises(ValidationError) as e:
        bad_timesheet = baker.prepare(TimeSheet, approved_at=timezone.now(), approved_by=None)
        bad_timesheet.save()

    assert "approved_at and approved_by must both be set" in str(e)

    with pytest.raises(ValidationError) as e:
        bad_timesheet = baker.prepare(TimeSheet, approved_at=None, approved_by=admin_user)
        bad_timesheet.save()

    assert "approved_at and approved_by must both be set" in str(e)


def test_facility_ticket_validate_resolved(admin_user):
    with pytest.raises(ValidationError) as e:
        bad_ticket_resolve = baker.prepare(
            FacilitySystemTicket, resolved=timezone.now(), resolved_by=None
        )
        bad_ticket_resolve.save()

    assert "resolved and resolved_by must both be set" in str(e)

    with pytest.raises(ValidationError) as e:
        bad_ticket_resolve = baker.prepare(
            FacilitySystemTicket, resolved=None, resolved_by=admin_user
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
