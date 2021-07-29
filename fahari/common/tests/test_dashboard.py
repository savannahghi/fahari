import random

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from model_bakery import baker

from fahari.common.constants import WHITELIST_COUNTIES
from fahari.common.dashboard import (
    get_active_facility_count,
    get_active_user_count,
    get_appointments_mtd,
    get_open_ticket_count,
)
from fahari.common.models import Facility
from fahari.ops.models import DailyUpdate, FacilitySystemTicket

User = get_user_model()

pytestmark = pytest.mark.django_db


def test_get_active_facility_count(user):
    baker.make(
        Facility,
        is_fahari_facility=True,
        operation_status="Operational",
        county=random.choice(WHITELIST_COUNTIES),
        active=True,
        organisation=user.organisation,
    )
    assert get_active_facility_count(user) == 1


def test_get_open_ticket_count(user):
    baker.make(
        FacilitySystemTicket,
        resolved=None,
        active=True,
        organisation=user.organisation,
    )
    assert get_open_ticket_count(user) == 1


def test_get_active_user_count(user):
    baker.make(
        User,
        is_approved=True,
        approval_notified=True,
        organisation=user.organisation,
    )
    assert get_active_user_count(user) >= 1


def test_get_appointments_mtd(user):
    today = timezone.datetime.today()
    baker.make(
        DailyUpdate,
        active=True,
        date=today,
        total=999,
        organisation=user.organisation,
    )
    assert get_appointments_mtd(user) == 999
