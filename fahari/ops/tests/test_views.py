import json
import random
import uuid

import pytest
from django.test import RequestFactory
from django.test.testcases import TestCase
from django.urls import reverse
from django.utils import timezone
from faker.proxy import Faker
from model_bakery import baker
from rest_framework import status

from fahari.common.constants import WHITELIST_COUNTIES
from fahari.common.models.common_models import Facility, System
from fahari.common.models.organisation_models import Organisation
from fahari.common.tests.test_api import LoggedInMixin
from fahari.ops.models import FacilitySystem, FacilitySystemTicket, TimeSheet, WeeklyProgramUpdate
from fahari.ops.views import (
    CommoditiesListView,
    FacilityDeviceRequestsListView,
    FacilityDevicesListView,
    FacilityNetworkStatusListView,
    FacilitySystemsView,
    FacilitySystemTicketsView,
    SecurityIncidentsListView,
    TimeSheetApproveView,
    UoMCategoryListView,
    UoMListView,
    WeeklyProgramUpdateCommentsView,
    WeeklyProgramUpdatesUpdateView,
    WeeklyProgramUpdatesView,
)

pytestmark = pytest.mark.django_db

fake = Faker()


def test_system_versions_view(user_with_all_permissions, client):
    client.force_login(user_with_all_permissions)
    url = reverse("ops:versions")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_tickets_view(user_with_all_permissions, client):
    client.force_login(user_with_all_permissions)
    url = reverse("ops:tickets")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_activity_log_view(user_with_all_permissions, client):
    client.force_login(user_with_all_permissions)
    url = reverse("ops:activity_logs")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_site_mentorship_view(user_with_all_permissions, client):
    client.force_login(user_with_all_permissions)
    url = reverse("ops:site_mentorships")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_daily_site_updates_view(user_with_all_permissions, client):
    client.force_login(user_with_all_permissions)
    url = reverse("ops:daily_site_updates")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_timesheets_view(user_with_all_permissions, client):
    client.force_login(user_with_all_permissions)
    url = reverse("ops:timesheets")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_weekly_program_updates_view(user_with_all_permissions, client):
    client.force_login(user_with_all_permissions)
    url = reverse("ops:weekly_program_updates")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_stock_receipt_verification_view(user_with_all_permissions, client):
    client.force_login(user_with_all_permissions)
    url = reverse("ops:stock_receipt_verifications")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_version_context_data():
    v = FacilitySystemsView()
    ctx = v.get_context_data()
    assert ctx["active"] == "facilities-nav"
    assert ctx["selected"] == "versions"


def test_tickets_context_data():
    v = FacilitySystemTicketsView()
    ctx = v.get_context_data()
    assert ctx["active"] == "facilities-nav"
    assert ctx["selected"] == "tickets"


def test_weekly_program_update_context_data():
    v = WeeklyProgramUpdatesView()
    ctx = v.get_context_data()
    assert ctx["active"] == "program-nav"
    assert ctx["selected"] == "weekly-program-updates"


class WeeklyProgramUpdateUpdateTest(LoggedInMixin, TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.facility = baker.make(
            Facility,
            is_fahari_facility=True,
            county=random.choice(WHITELIST_COUNTIES),
            operation_status="Operational",
            organisation=self.global_organisation,
        )
        self.program_update = baker.make(
            WeeklyProgramUpdate,
            organisation=self.global_organisation,
            facility=self.facility,
            operation_area=WeeklyProgramUpdate.OperationGroup.ADMIN.value,
            status=WeeklyProgramUpdate.TaskStatus.IN_PROGRESS.value,
            assigned_persons=json.dumps([fake.name(), fake.name()]),
            date_created=timezone.now().isoformat(),
        )
        super().setUp()

    def test_weekly_program_updates_update_context_data(self, **kwargs):
        request = RequestFactory().get(
            reverse("ops:weekly_program_updates_update", kwargs={"pk": self.program_update.pk}),
        )
        request.user = self.user
        view = WeeklyProgramUpdatesUpdateView()
        view.setup(request, pk=self.program_update.pk)
        view.dispatch(request, pk=self.program_update.pk)
        context = view.get_context_data()
        self.assertIn("create_comments_form", context)


def test_weekly_program_update_comment_context_data():
    v = WeeklyProgramUpdateCommentsView()
    ctx = v.get_context_data()
    assert ctx["active"] == "program-nav"
    assert ctx["selected"] == "weekly-program-update-comments"


def test_timesheet_approve_view_happy_case(request_with_user):
    assert request_with_user.user is not None
    timesheet = baker.make(TimeSheet, approved_by=None, approved_at=None)
    view = TimeSheetApproveView()
    resp = view.post(request_with_user, pk=timesheet.pk)
    assert resp.status_code == 302

    timesheet.refresh_from_db()
    assert timesheet.approved_by is not None
    assert timesheet.approved_at is not None


def test_timesheet_approve_view_error_case(request_with_user):
    fake_pk = uuid.uuid4()
    view = TimeSheetApproveView()
    resp = view.post(request_with_user, pk=fake_pk)
    assert resp.status_code == 200  # page re-rendered with an error


def test_ticket_resolve_view_get(user_with_all_permissions, client):
    org = baker.make(Organisation)
    facility = baker.make(Facility, organisation=org, name="Test")
    system = baker.make(System, organisation=org, name="System")
    vrs = "0.0.1"
    facility_system = baker.make(
        FacilitySystem,
        facility=facility,
        system=system,
        version=vrs,
        trainees=json.dumps([fake.name(), fake.name()]),
    )
    client.force_login(user_with_all_permissions)
    open_ticket = baker.make(
        FacilitySystemTicket, facility_system=facility_system, resolved=None, resolved_by=None
    )
    url = reverse("ops:ticket_resolve", args=[open_ticket.pk])
    response = client.get(url, format="json")
    assert response.status_code == 200


def test_ticket_resolve_view_post(user_with_all_permissions, client):
    org = baker.make(Organisation)
    facility = baker.make(Facility, organisation=org, name="Test")
    system = baker.make(System, organisation=org, name="System")
    vrs = "0.0.1"
    facility_system = baker.make(
        FacilitySystem,
        facility=facility,
        system=system,
        version=vrs,
        trainees=json.dumps([fake.name(), fake.name()]),
    )
    client.force_login(user_with_all_permissions)
    open_ticket = baker.make(
        FacilitySystemTicket, facility_system=facility_system, resolved=None, resolved_by=None
    )
    url = reverse("ops:ticket_resolve", args=[open_ticket.pk])
    response = client.post(url, None, format="json")
    assert response.status_code == 302

    open_ticket.refresh_from_db()
    assert open_ticket.resolved is not None
    assert open_ticket.resolved_by is not None
    assert open_ticket.resolve_note == ""


def test_ticket_resolve_view_post_with_note(user_with_all_permissions, client):
    org = baker.make(Organisation)
    facility = baker.make(Facility, organisation=org, name="Test")
    system = baker.make(System, organisation=org, name="System")
    vrs = "0.0.1"
    facility_system = baker.make(
        FacilitySystem,
        facility=facility,
        system=system,
        version=vrs,
        trainees=json.dumps([fake.name(), fake.name()]),
    )
    client.force_login(user_with_all_permissions)
    open_ticket = baker.make(
        FacilitySystemTicket, facility_system=facility_system, resolved=None, resolved_by=None
    )
    url = reverse("ops:ticket_resolve", args=[open_ticket.pk])
    data = {"resolve_note": "All issues solved ..."}
    response = client.post(url, data, format="json")
    assert response.status_code == 302

    open_ticket.refresh_from_db()
    assert open_ticket.resolved is not None
    assert open_ticket.resolved_by is not None
    assert open_ticket.resolve_note == data["resolve_note"]


def test_commodities_context_data():
    v = CommoditiesListView()
    ctx = v.get_context_data()
    assert ctx["active"] == "inventory-nav"
    assert ctx["selected"] == "commodities"


def test_uoms_context_data():
    v = UoMListView()
    ctx = v.get_context_data()
    assert ctx["active"] == "inventory-nav"
    assert ctx["selected"] == "uoms"


def test_uom_categories_context_data():
    v = UoMCategoryListView()
    ctx = v.get_context_data()
    assert ctx["active"] == "inventory-nav"
    assert ctx["selected"] == "uom_categories"


def test_network_status_context_data():
    v = FacilityNetworkStatusListView()
    ctx = v.get_context_data()
    assert ctx["active"] == "hardware-network-nav"
    assert ctx["selected"] == "facility_network_status"


def test_facility_devices_context_data():
    v = FacilityDevicesListView()
    ctx = v.get_context_data()
    assert ctx["active"] == "hardware-network-nav"
    assert ctx["selected"] == "facility_devices"


def test_facility_device_request_context_data():
    v = FacilityDeviceRequestsListView()
    ctx = v.get_context_data()
    assert ctx["active"] == "hardware-network-nav"
    assert ctx["selected"] == "facility_device_requests"


def test_security_incidence_context_data():
    v = SecurityIncidentsListView()
    ctx = v.get_context_data()
    assert ctx["active"] == "hardware-network-nav"
    assert ctx["selected"] == "security_incidents"


def test_facility_network_status_view(user_with_all_permissions, client):
    client.force_login(user_with_all_permissions)
    url = reverse("ops:facility_network_status")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_facility_device_view(user_with_all_permissions, client):
    client.force_login(user_with_all_permissions)
    url = reverse("ops:facility_devices")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_facility_device_request_view(user_with_all_permissions, client):
    client.force_login(user_with_all_permissions)
    url = reverse("ops:facility_device_requests")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_security_incidence_view(user_with_all_permissions, client):
    client.force_login(user_with_all_permissions)
    url = reverse("ops:security_incidents")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
