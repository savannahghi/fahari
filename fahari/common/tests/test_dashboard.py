import json
import random

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker.proxy import Faker
from model_bakery import baker

from fahari.common.constants import WHITELIST_COUNTIES
from fahari.common.dashboard import (
    get_active_facility_count,
    get_active_user_count,
    get_appointments_mtd,
    get_open_ticket_count,
)
from fahari.common.models import Facility, Organisation
from fahari.common.models.common_models import System
from fahari.ops.models import DailyUpdate, FacilitySystem, FacilitySystemTicket

User = get_user_model()

pytestmark = pytest.mark.django_db

fake = Faker()


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
    org = baker.make(Organisation)
    facility = baker.make(Facility, organisation=org, name="Test")
    system = baker.make(System, organisation=org, name="System")
    vrs = "0.0.1"
    facility_system = baker.make(
        FacilitySystem,
        facility=facility,
        system=system,
        version=vrs,
        organisation=org,
        trainees=json.dumps([fake.name(), fake.name()]),
    )
    baker.make(
        FacilitySystemTicket,
        facility_system=facility_system,
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
