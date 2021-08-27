import json
import random
from datetime import date

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from faker import Faker
from model_bakery import baker
from rest_framework.test import APITestCase

from fahari.common.constants import WHITELIST_COUNTIES
from fahari.common.models import Facility, System
from fahari.common.tests.test_api import LoggedInMixin
from fahari.ops.forms import FacilitySystemTicketForm
from fahari.ops.models import (
    ActivityLog,
    Commodity,
    DailyUpdate,
    FacilitySystem,
    FacilitySystemTicket,
    SiteMentorship,
    StockReceiptVerification,
    TimeSheet,
    WeeklyProgramUpdate,
    default_commodity,
)

fake = Faker()


class FacilitySystemViewsetTest(LoggedInMixin, APITestCase):
    def setUp(self):
        self.url_list = reverse("api:facilitysystem-list")
        self.facility = baker.make(Facility, organisation=self.global_organisation)
        self.system = baker.make(System, organisation=self.global_organisation)
        super().setUp()

    def test_create(self):
        data = {
            "facility": self.facility.pk,
            "system": self.system.pk,
            "version": fake.name()[:63],
            "organisation": self.global_organisation.pk,
        }
        response = self.client.post(self.url_list, data)
        assert response.status_code == 201, response.json()
        assert response.data["version"] == data["version"]

    def test_retrieve(self):
        instance = baker.make(
            FacilitySystem,
            organisation=self.global_organisation,
        )
        response = self.client.get(self.url_list)
        assert response.status_code == 200, response.json()
        assert response.data["count"] >= 1, response.json()

        versions = [a["version"] for a in response.data["results"]]
        assert instance.version in versions

    def test_patch_system(self):
        instance = baker.make(
            FacilitySystem,
            organisation=self.global_organisation,
        )
        edit = {"version": fake.name()[:63]}
        url = reverse("api:facilitysystem-detail", kwargs={"pk": instance.pk})
        response = self.client.patch(url, edit)

        assert response.status_code == 200, response.json()
        assert response.data["version"] == edit["version"]

    def test_put_system(self):
        instance = baker.make(
            FacilitySystem,
            organisation=self.global_organisation,
        )
        data = {
            "facility": self.facility.pk,
            "system": self.system.pk,
            "version": fake.name()[:63],
            "organisation": self.global_organisation.pk,
        }
        url = reverse("api:facilitysystem-detail", kwargs={"pk": instance.pk})
        response = self.client.put(url, data)

        assert response.status_code == 200, response.json()
        assert response.data["version"] == data["version"]


class FacilitySystemFormTest(LoggedInMixin, TestCase):
    def setUp(self):
        self.user = baker.make(settings.AUTH_USER_MODEL, email=fake.email())
        self.facility = baker.make(
            Facility,
            is_fahari_facility=True,
            county=random.choice(WHITELIST_COUNTIES),
            operation_status="Operational",
            organisation=self.global_organisation,
        )
        self.system = baker.make(System, organisation=self.global_organisation)
        super().setUp()

    def test_facilitysystem_form_init(self):
        baker.make(FacilitySystem, organisation=self.global_organisation)
        form = FacilitySystemTicketForm()
        queryset = form.fields["facility_system"].queryset
        assert FacilitySystem.objects.count() > 0
        assert queryset.count() == 0

    def test_create(self):
        data = {
            "facility": self.facility.pk,
            "system": self.system.pk,
            "version": fake.name()[:63],
            "organisation": self.global_organisation.pk,
        }
        response = self.client.post(reverse("ops:version_create"), data=data)
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_update(self):
        instance = baker.make(
            FacilitySystem,
            organisation=self.global_organisation,
        )
        data = {
            "pk": instance.pk,
            "facility": self.facility.pk,
            "system": self.system.pk,
            "version": fake.name()[:63],
            "organisation": self.global_organisation.pk,
        }
        response = self.client.post(
            reverse("ops:version_update", kwargs={"pk": instance.pk}), data=data
        )
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_delete(self):
        instance = baker.make(
            FacilitySystem,
            organisation=self.global_organisation,
        )
        response = self.client.post(
            reverse("ops:version_delete", kwargs={"pk": instance.pk}),
        )
        self.assertEqual(
            response.status_code,
            302,
        )


class FacilitySystemTicketViewsetTest(LoggedInMixin, APITestCase):
    def setUp(self):
        self.url_list = reverse("api:facilitysystemticket-list")
        self.facility = baker.make(Facility, organisation=self.global_organisation)
        self.system = baker.make(System, organisation=self.global_organisation)
        self.facility_system = baker.make(
            FacilitySystem,
            facility=self.facility,
            system=self.system,
            organisation=self.global_organisation,
        )
        super().setUp()

    def test_create(self):
        data = {
            "facility_system": self.facility_system.pk,
            "details": fake.text(),
            "raised_by": fake.name(),
            "organisation": self.global_organisation.pk,
        }
        response = self.client.post(self.url_list, data)
        assert response.status_code == 201, response.json()
        assert response.data["details"] == data["details"]

    def test_retrieve(self):
        instance = baker.make(
            FacilitySystemTicket,
            facility_system=self.facility_system,
            details=fake.text(),
            raised_by=fake.name(),
            organisation=self.global_organisation,
        )
        response = self.client.get(self.url_list)
        assert response.status_code == 200, response.json()
        assert response.data["count"] >= 1, response.json()

        details = [a["details"] for a in response.data["results"]]
        assert instance.details in details

    def test_patch_system(self):
        instance = baker.make(
            FacilitySystemTicket,
            facility_system=self.facility_system,
            details=fake.text(),
            raised_by=fake.name(),
            organisation=self.global_organisation,
        )
        edit = {"raised_by": fake.name()}
        url = reverse("api:facilitysystemticket-detail", kwargs={"pk": instance.pk})
        response = self.client.patch(url, edit)

        assert response.status_code == 200, response.json()
        assert response.data["raised_by"] == edit["raised_by"]

    def test_put_system(self):
        instance = baker.make(
            FacilitySystemTicket,
            facility_system=self.facility_system,
            details=fake.text(),
            raised_by=fake.name(),
            organisation=self.global_organisation,
        )
        data = {
            "facility_system": self.facility_system.pk,
            "details": fake.text(),
            "raised_by": fake.name(),
            "organisation": self.global_organisation.pk,
        }
        url = reverse("api:facilitysystemticket-detail", kwargs={"pk": instance.pk})
        response = self.client.put(url, data)

        assert response.status_code == 200, response.json()
        assert response.data["details"] == data["details"]


class FacilitySystemTicketFormTest(LoggedInMixin, TestCase):
    def setUp(self):
        self.facility = baker.make(
            Facility,
            is_fahari_facility=True,
            county=random.choice(WHITELIST_COUNTIES),
            operation_status="Operational",
            organisation=self.global_organisation,
        )
        self.system = baker.make(System, organisation=self.global_organisation)
        self.facility_system = baker.make(
            FacilitySystem,
            facility=self.facility,
            system=self.system,
            organisation=self.global_organisation,
        )
        super().setUp()

    def test_create(self):
        data = {
            "facility_system": self.facility_system.pk,
            "details": fake.text(),
            "raised": timezone.now().isoformat(),
            "raised_by": fake.name(),
            "organisation": self.global_organisation.pk,
        }
        response = self.client.post(reverse("ops:ticket_create"), data=data)
        self.assertEqual(
            response.status_code,
            200,
        )

    def test_update(self):
        instance = baker.make(
            FacilitySystemTicket,
            facility_system=self.facility_system,
            details=fake.text(),
            raised_by=fake.name(),
            organisation=self.global_organisation,
        )
        data = {
            "pk": instance.pk,
            "facility_system": self.facility_system.pk,
            "details": fake.text(),
            "raised": timezone.now().isoformat(),
            "raised_by": fake.name(),
            "organisation": self.global_organisation.pk,
        }
        response = self.client.post(
            reverse("ops:ticket_update", kwargs={"pk": instance.pk}), data=data
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_delete(self):
        instance = baker.make(
            FacilitySystemTicket,
            facility_system=self.facility_system,
            details=fake.text(),
            raised_by=fake.name(),
            organisation=self.global_organisation,
        )
        response = self.client.post(
            reverse("ops:ticket_delete", kwargs={"pk": instance.pk}),
        )
        self.assertEqual(
            response.status_code,
            302,
        )


class StockReceiptsViewsetTest(LoggedInMixin, APITestCase):
    def setUp(self):
        self.url_list = reverse("api:stockreceiptverification-list")
        self.detail_url_name = "api:stockreceiptverification-detail"
        self.facility = baker.make(
            Facility,
            is_fahari_facility=True,
            county=random.choice(WHITELIST_COUNTIES),
            organisation=self.global_organisation,
        )
        super().setUp()

    def test_create(self):
        data = {
            "facility": self.facility.pk,
            "description": fake.text(),
            "pack_size": fake.text(),
            "delivery_note_number": fake.name()[:63],
            "quantity_received": "10.0",
            "batch_number": fake.name()[:63],
            "expiry_date": date.today().isoformat(),
            "comments": fake.text(),
            "organisation": self.global_organisation.pk,
        }
        response = self.client.post(self.url_list, data)
        assert response.status_code == 201, response.json()
        assert response.data["facility"] == data["facility"]

    def test_retrieve(self):
        instance = baker.make(
            StockReceiptVerification,
            facility=self.facility,
            organisation=self.global_organisation,
        )
        response = self.client.get(self.url_list)
        assert response.status_code == 200, response.json()
        assert response.data["count"] >= 1, response.json()

        facilities = [a["facility"] for a in response.data["results"]]
        assert instance.facility.pk in facilities

    def test_patch(self):
        instance = baker.make(
            StockReceiptVerification,
            facility=self.facility,
            organisation=self.global_organisation,
        )
        edit = {"active": False}
        url = reverse(self.detail_url_name, kwargs={"pk": instance.pk})
        response = self.client.patch(url, edit)

        assert response.status_code == 200, response.json()
        assert response.data["active"] == edit["active"]

    def test_put(self):
        instance = baker.make(
            StockReceiptVerification,
            facility=self.facility,
            organisation=self.global_organisation,
        )
        data = {
            "facility": self.facility.pk,
            "description": fake.text(),
            "pack_size": fake.text(),
            "delivery_note_number": fake.name()[:63],
            "quantity_received": "10.0",
            "batch_number": fake.name()[:63],
            "expiry_date": date.today().isoformat(),
            "comments": fake.text(),
            "organisation": self.global_organisation.pk,
            "active": False,
        }
        url = reverse(self.detail_url_name, kwargs={"pk": instance.pk})
        response = self.client.put(url, data)

        assert response.status_code == 200, response.json()
        assert response.data["active"] == data["active"]


class StockReceiptsFormTest(LoggedInMixin, TestCase):
    def setUp(self):
        self.facility = baker.make(
            Facility,
            is_fahari_facility=True,
            county=random.choice(WHITELIST_COUNTIES),
            organisation=self.global_organisation,
        )
        self.default_commodity = default_commodity()
        super().setUp()

    def test_create(self):
        data = {
            "facility": self.facility.pk,
            "description": fake.text(),
            "pack_size": fake.text(),
            "delivery_note_number": fake.name()[:63],
            "quantity_received": "10.0",
            "batch_number": fake.name()[:63],
            "expiry_date": date.today().isoformat(),
            "delivery_date": date.today().isoformat(),
            "comments": fake.text(),
            "organisation": self.global_organisation.pk,
            "commodity": self.default_commodity,
            "active": False,
        }
        response = self.client.post(reverse("ops:stock_receipt_verification_create"), data=data)
        print(response.content)
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_update(self):
        instance = baker.make(
            StockReceiptVerification,
            facility=self.facility,
            organisation=self.global_organisation,
        )
        data = {
            "pk": instance.pk,
            "facility": self.facility.pk,
            "description": fake.text(),
            "pack_size": fake.text(),
            "delivery_note_number": fake.name()[:63],
            "quantity_received": "10.0",
            "batch_number": fake.name()[:63],
            "expiry_date": date.today().isoformat(),
            "delivery_date": date.today().isoformat(),
            "comments": fake.text(),
            "organisation": self.global_organisation.pk,
            "commodity": self.default_commodity,
            "active": False,
        }
        response = self.client.post(
            reverse("ops:stock_receipt_verification_update", kwargs={"pk": instance.pk}), data=data
        )
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_delete(self):
        instance = baker.make(
            StockReceiptVerification,
            facility=self.facility,
            organisation=self.global_organisation,
        )
        response = self.client.post(
            reverse("ops:stock_receipt_verification_delete", kwargs={"pk": instance.pk}),
        )
        self.assertEqual(
            response.status_code,
            302,
        )


class ActivityLogViewsetTest(LoggedInMixin, APITestCase):
    def setUp(self):
        self.url_list = reverse("api:activitylog-list")
        self.detail_url_name = "api:activitylog-detail"
        super().setUp()

    def test_create(self):
        data = {
            "activity": fake.text(),
            "planned_date": date.today().isoformat(),
            "requested_date": date.today().isoformat(),
            "procurement_date": date.today().isoformat(),
            "finance_approval_date": date.today().isoformat(),
            "final_approval_date": date.today().isoformat(),
            "done_date": date.today().isoformat(),
            "invoiced_date": date.today().isoformat(),
            "remarks": fake.text(),
            "organisation": self.global_organisation.pk,
        }
        response = self.client.post(self.url_list, data)
        assert response.status_code == 201, response.json()
        assert response.data["activity"] == data["activity"]

    def test_retrieve(self):
        instance = baker.make(
            ActivityLog,
            organisation=self.global_organisation,
        )
        response = self.client.get(self.url_list)
        assert response.status_code == 200, response.json()
        assert response.data["count"] >= 1, response.json()

        ids = [a["id"] for a in response.data["results"]]
        assert str(instance.pk) in ids

    def test_patch(self):
        instance = baker.make(
            ActivityLog,
            organisation=self.global_organisation,
        )
        edit = {"active": False}
        url = reverse(self.detail_url_name, kwargs={"pk": instance.pk})
        response = self.client.patch(url, edit)

        assert response.status_code == 200, response.json()
        assert response.data["active"] == edit["active"]

    def test_put(self):
        instance = baker.make(
            ActivityLog,
            organisation=self.global_organisation,
        )
        data = {
            "activity": fake.text(),
            "planned_date": date.today().isoformat(),
            "requested_date": date.today().isoformat(),
            "procurement_date": date.today().isoformat(),
            "finance_approval_date": date.today().isoformat(),
            "final_approval_date": date.today().isoformat(),
            "done_date": date.today().isoformat(),
            "invoiced_date": date.today().isoformat(),
            "remarks": fake.text(),
            "organisation": self.global_organisation.pk,
            "active": False,
        }
        url = reverse(self.detail_url_name, kwargs={"pk": instance.pk})
        response = self.client.put(url, data)

        assert response.status_code == 200, response.json()
        assert response.data["active"] == data["active"]


class ActivityLogFormTest(LoggedInMixin, TestCase):
    def test_create(self):
        data = {
            "activity": fake.text(),
            "planned_date": date.today().isoformat(),
            "requested_date": date.today().isoformat(),
            "procurement_date": date.today().isoformat(),
            "finance_approval_date": date.today().isoformat(),
            "final_approval_date": date.today().isoformat(),
            "done_date": date.today().isoformat(),
            "invoiced_date": date.today().isoformat(),
            "remarks": fake.text(),
            "organisation": self.global_organisation.pk,
        }
        response = self.client.post(reverse("ops:activity_log_create"), data=data)
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_update(self):
        instance = baker.make(
            ActivityLog,
            organisation=self.global_organisation,
        )
        data = {
            "pk": instance.pk,
            "activity": fake.text(),
            "planned_date": date.today().isoformat(),
            "requested_date": date.today().isoformat(),
            "procurement_date": date.today().isoformat(),
            "finance_approval_date": date.today().isoformat(),
            "final_approval_date": date.today().isoformat(),
            "done_date": date.today().isoformat(),
            "invoiced_date": date.today().isoformat(),
            "remarks": fake.text(),
            "active": False,
        }
        response = self.client.post(
            reverse("ops:activity_log_update", kwargs={"pk": instance.pk}), data=data
        )
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_delete(self):
        instance = baker.make(
            ActivityLog,
            organisation=self.global_organisation,
        )
        response = self.client.post(
            reverse("ops:activity_log_delete", kwargs={"pk": instance.pk}),
        )
        self.assertEqual(
            response.status_code,
            302,
        )


class SiteMentorshipViewsetTest(LoggedInMixin, APITestCase):
    def setUp(self):
        self.url_list = reverse("api:sitementorship-list")
        self.detail_url_name = "api:sitementorship-detail"
        self.facility = baker.make(
            Facility,
            is_fahari_facility=True,
            county=random.choice(WHITELIST_COUNTIES),
            organisation=self.global_organisation,
        )
        super().setUp()

    def test_create(self):
        data = {
            "staff_member": self.user.pk,
            "site": self.facility.pk,
            "day": date.today().isoformat(),
            "objective": fake.text(),
            "pick_up_point": fake.text(),
            "drop_off_point": fake.text(),
            "organisation": self.global_organisation.pk,
        }
        response = self.client.post(self.url_list, data)
        assert response.status_code == 201, response.json()
        assert response.data["objective"] == data["objective"]

    def test_retrieve(self):
        instance = baker.make(
            SiteMentorship,
            site=self.facility,
            staff_member=self.user,
            organisation=self.global_organisation,
        )
        response = self.client.get(self.url_list)
        assert response.status_code == 200, response.json()
        assert response.data["count"] >= 1, response.json()

        facilities = [a["id"] for a in response.data["results"]]
        assert str(instance.pk) in facilities

    def test_patch(self):
        instance = baker.make(
            SiteMentorship,
            site=self.facility,
            staff_member=self.user,
            organisation=self.global_organisation,
        )
        edit = {"active": False}
        url = reverse(self.detail_url_name, kwargs={"pk": instance.pk})
        response = self.client.patch(url, edit)

        assert response.status_code == 200, response.json()
        assert response.data["active"] == edit["active"]

    def test_put(self):
        instance = baker.make(
            SiteMentorship,
            site=self.facility,
            organisation=self.global_organisation,
        )
        data = {
            "staff_member": self.user.pk,
            "site": self.facility.pk,
            "day": date.today().isoformat(),
            "objective": fake.text(),
            "pick_up_point": fake.text(),
            "drop_off_point": fake.text(),
            "organisation": self.global_organisation.pk,
            "active": False,
        }
        url = reverse(self.detail_url_name, kwargs={"pk": instance.pk})
        response = self.client.put(url, data)

        assert response.status_code == 200, response.json()
        assert response.data["active"] == data["active"]


class SiteMentorshipFormTest(LoggedInMixin, TestCase):
    def setUp(self):
        self.facility = baker.make(
            Facility,
            is_fahari_facility=True,
            county=random.choice(WHITELIST_COUNTIES),
            organisation=self.global_organisation,
        )
        super().setUp()

    def test_create(self):
        data = {
            "staff_member": self.user.pk,
            "site": self.facility.pk,
            "day": date.today().isoformat(),
            "duration": "08:00:00",
            "objective": fake.text(),
            "pick_up_point": fake.text(),
            "drop_off_point": fake.text(),
            "organisation": self.global_organisation.pk,
        }
        response = self.client.post(reverse("ops:site_mentorship_create"), data=data)
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_update(self):
        instance = baker.make(
            SiteMentorship,
            site=self.facility,
            staff_member=self.user,
            organisation=self.global_organisation,
        )
        data = {
            "pk": instance.pk,
            "staff_member": self.user.pk,
            "site": self.facility.pk,
            "day": date.today().isoformat(),
            "duration": "08:00:00",
            "objective": fake.text(),
            "pick_up_point": fake.text(),
            "drop_off_point": fake.text(),
            "organisation": self.global_organisation.pk,
            "active": False,
        }
        response = self.client.post(
            reverse("ops:site_mentorship_update", kwargs={"pk": instance.pk}), data=data
        )
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_delete(self):
        instance = baker.make(
            SiteMentorship,
            site=self.facility,
            staff_member=self.user,
            organisation=self.global_organisation,
        )
        response = self.client.post(
            reverse("ops:site_mentorship_delete", kwargs={"pk": instance.pk}),
        )
        self.assertEqual(
            response.status_code,
            302,
        )


class DailyUpdateViewsetTest(LoggedInMixin, APITestCase):
    def setUp(self):
        self.url_list = reverse("api:dailyupdate-list")
        self.detail_url_name = "api:dailyupdate-detail"
        self.facility = baker.make(
            Facility,
            is_fahari_facility=True,
            county=random.choice(WHITELIST_COUNTIES),
            organisation=self.global_organisation,
        )
        super().setUp()

    def test_create(self):
        data = {
            "facility": self.facility.pk,
            "date": date.today().isoformat(),
            "total": 10,
            "clients_booked": 8,
            "kept_appointment": 7,
            "missed_appointment": 1,
            "came_early": 0,
            "unscheduled": 2,
            "new_ft": 0,
            "ipt_new_adults": 0,
            "ipt_new_paeds": 0,
            "organisation": self.global_organisation.pk,
        }
        response = self.client.post(self.url_list, data)
        assert response.status_code == 201, response.json()
        assert response.data["facility"] == data["facility"]

    def test_retrieve(self):
        instance = baker.make(
            DailyUpdate,
            facility=self.facility,
            organisation=self.global_organisation,
        )
        response = self.client.get(self.url_list)
        assert response.status_code == 200, response.json()
        assert response.data["count"] >= 1, response.json()

        facilities = [a["id"] for a in response.data["results"]]
        assert str(instance.pk) in facilities

    def test_patch(self):
        instance = baker.make(
            DailyUpdate,
            facility=self.facility,
            organisation=self.global_organisation,
        )
        edit = {"active": False}
        url = reverse(self.detail_url_name, kwargs={"pk": instance.pk})
        response = self.client.patch(url, edit)

        assert response.status_code == 200, response.json()
        assert response.data["active"] == edit["active"]

    def test_put(self):
        instance = baker.make(
            DailyUpdate,
            facility=self.facility,
            organisation=self.global_organisation,
        )
        data = {
            "facility": self.facility.pk,
            "date": date.today().isoformat(),
            "total": 10,
            "clients_booked": 8,
            "kept_appointment": 7,
            "missed_appointment": 1,
            "came_early": 0,
            "unscheduled": 2,
            "new_ft": 0,
            "ipt_new_adults": 0,
            "ipt_new_paeds": 0,
            "organisation": self.global_organisation.pk,
            "active": False,
        }
        url = reverse(self.detail_url_name, kwargs={"pk": instance.pk})
        response = self.client.put(url, data)

        assert response.status_code == 200, response.json()
        assert response.data["active"] == data["active"]


class DailyUpdateFormTest(LoggedInMixin, TestCase):
    def setUp(self):
        self.facility = baker.make(
            Facility,
            is_fahari_facility=True,
            county=random.choice(WHITELIST_COUNTIES),
            organisation=self.global_organisation,
        )
        super().setUp()

    def test_create(self):
        data = {
            "facility": self.facility.pk,
            "date": date.today().isoformat(),
            "total": 10,
            "clients_booked": 8,
            "kept_appointment": 7,
            "missed_appointment": 1,
            "came_early": 0,
            "unscheduled": 2,
            "new_ft": 0,
            "ipt_new_adults": 0,
            "ipt_new_paeds": 0,
            "organisation": self.global_organisation.pk,
        }
        response = self.client.post(reverse("ops:daily_update_create"), data=data)
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_update(self):
        instance = baker.make(
            DailyUpdate,
            facility=self.facility,
            organisation=self.global_organisation,
        )
        data = {
            "facility": self.facility.pk,
            "date": date.today().isoformat(),
            "total": 10,
            "clients_booked": 8,
            "kept_appointment": 7,
            "missed_appointment": 1,
            "came_early": 0,
            "unscheduled": 2,
            "new_ft": 0,
            "ipt_new_adults": 0,
            "ipt_new_paeds": 0,
            "organisation": self.global_organisation.pk,
            "active": False,
        }
        response = self.client.post(
            reverse("ops:daily_update_update", kwargs={"pk": instance.pk}), data=data
        )
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_delete(self):
        instance = baker.make(
            DailyUpdate,
            facility=self.facility,
            organisation=self.global_organisation,
        )
        response = self.client.post(
            reverse("ops:daily_update_delete", kwargs={"pk": instance.pk}),
        )
        self.assertEqual(
            response.status_code,
            302,
        )


class TimeSheetViewsetTest(LoggedInMixin, APITestCase):
    def setUp(self):
        self.url_list = reverse("api:timesheet-list")
        self.detail_url_name = "api:timesheet-detail"
        super().setUp()

    def test_create(self):
        data = {
            "staff": self.user.pk,
            "date": date.today().isoformat(),
            "activity": fake.text(),
            "output": fake.text(),
            "hours": random.randint(1, 10),
            "location": fake.text(),
            "organisation": self.global_organisation.pk,
        }
        response = self.client.post(self.url_list, data)
        assert response.status_code == 201, response.json()
        assert response.data["staff"] == data["staff"]

    def test_retrieve(self):
        instance = baker.make(
            TimeSheet,
            staff=self.user,
            organisation=self.global_organisation,
        )
        response = self.client.get(self.url_list)
        assert response.status_code == 200, response.json()
        assert response.data["count"] >= 1, response.json()

        ids = [a["id"] for a in response.data["results"]]
        assert str(instance.pk) in ids

    def test_patch(self):
        instance = baker.make(
            TimeSheet,
            staff=self.user,
            organisation=self.global_organisation,
        )
        edit = {"active": False}
        url = reverse(self.detail_url_name, kwargs={"pk": instance.pk})
        response = self.client.patch(url, edit)

        assert response.status_code == 200, response.json()
        assert response.data["active"] == edit["active"]

    def test_put(self):
        instance = baker.make(
            TimeSheet,
            staff=self.user,
            organisation=self.global_organisation,
        )
        data = {
            "staff": self.user.pk,
            "date": date.today().isoformat(),
            "activity": fake.text(),
            "output": fake.text(),
            "hours": random.randint(1, 10),
            "location": fake.text(),
            "organisation": self.global_organisation.pk,
            "active": False,
        }
        url = reverse(self.detail_url_name, kwargs={"pk": instance.pk})
        response = self.client.put(url, data)

        assert response.status_code == 200, response.json()
        assert response.data["active"] == data["active"]


class TimeSheetFormTest(LoggedInMixin, TestCase):
    def test_create(self):
        data = {
            "staff": self.user.pk,
            "date": date.today().isoformat(),
            "activity": fake.text(),
            "output": fake.text(),
            "hours": random.randint(1, 10),
            "location": fake.text(),
            "organisation": self.global_organisation.pk,
        }
        response = self.client.post(reverse("ops:timesheet_create"), data=data)
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_update(self):
        instance = baker.make(
            TimeSheet,
            staff=self.user,
            organisation=self.global_organisation,
        )
        data = {
            "staff": self.user.pk,
            "date": date.today().isoformat(),
            "activity": fake.text(),
            "output": fake.text(),
            "hours": random.randint(1, 10),
            "location": fake.text(),
            "organisation": self.global_organisation.pk,
            "active": False,
        }
        response = self.client.post(
            reverse("ops:timesheet_update", kwargs={"pk": instance.pk}), data=data
        )
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_delete(self):
        instance = baker.make(
            TimeSheet,
            staff=self.user,
            organisation=self.global_organisation,
        )
        response = self.client.post(
            reverse("ops:timesheet_delete", kwargs={"pk": instance.pk}),
        )
        self.assertEqual(
            response.status_code,
            302,
        )


class WeeklyProgramUpdateViewsetTest(LoggedInMixin, APITestCase):
    def setUp(self):
        self.url_list = reverse("api:weeklyprogramupdate-list")
        self.detail_url_name = "api:weeklyprogramupdate-detail"
        super().setUp()

    def test_create(self):
        data = {
            "date": date.today().isoformat(),
            "attendees": json.dumps([fake.name(), fake.name()]),
            "organisation": self.global_organisation.pk,
            "description": "-",
        }
        response = self.client.post(self.url_list, data)
        assert response.status_code == 201, response.json()
        assert response.data["date"] == data["date"]

    def test_retrieve(self):
        instance = baker.make(
            WeeklyProgramUpdate,
            attendees=json.dumps([fake.name(), fake.name()]),
            organisation=self.global_organisation,
        )
        response = self.client.get(self.url_list)
        assert response.status_code == 200, response.json()
        assert response.data["count"] >= 1, response.json()

        ids = [a["id"] for a in response.data["results"]]
        assert str(instance.pk) in ids

    def test_patch(self):
        instance = baker.make(
            WeeklyProgramUpdate,
            attendees=json.dumps([fake.name(), fake.name()]),
            organisation=self.global_organisation,
        )
        edit = {"active": False}
        url = reverse(self.detail_url_name, kwargs={"pk": instance.pk})
        response = self.client.patch(url, edit)

        assert response.status_code == 200, response.json()
        assert response.data["active"] == edit["active"]

    def test_put(self):
        instance = baker.make(
            WeeklyProgramUpdate,
            attendees=json.dumps([fake.name(), fake.name()]),
            organisation=self.global_organisation,
        )
        data = {
            "date": date.today().isoformat(),
            "attendees": f"{fake.name()},{fake.name()}",
            "organisation": self.global_organisation.pk,
            "active": False,
        }
        url = reverse(self.detail_url_name, kwargs={"pk": instance.pk})
        response = self.client.put(url, data)

        assert response.status_code == 200, response.json()
        assert response.data["active"] == data["active"]


class WeeklyProgramUpdateFormTest(LoggedInMixin, TestCase):
    def test_create(self):
        data = {
            "date": date.today().isoformat(),
            "attendees": json.dumps([fake.name(), fake.name()]),
            "organisation": self.global_organisation.pk,
            "notes": "-",
        }
        response = self.client.post(reverse("ops:weekly_program_updates_create"), data=data)
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_update(self):
        instance = baker.make(
            WeeklyProgramUpdate,
            attendees=json.dumps([fake.name(), fake.name()]),
            organisation=self.global_organisation,
        )
        data = {
            "date": date.today().isoformat(),
            "attendees": f"{fake.name()},{fake.name()}",
            "organisation": self.global_organisation.pk,
            "notes": "-",
        }
        response = self.client.post(
            reverse("ops:weekly_program_updates_update", kwargs={"pk": instance.pk}), data=data
        )
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_delete(self):
        instance = baker.make(
            WeeklyProgramUpdate,
            attendees=json.dumps([fake.name(), fake.name()]),
            organisation=self.global_organisation,
        )
        response = self.client.post(
            reverse("ops:weekly_program_updates_delete", kwargs={"pk": instance.pk}),
        )
        self.assertEqual(
            response.status_code,
            302,
        )


class CommodityViewsetTest(LoggedInMixin, APITestCase):
    def setUp(self):
        self.url_list = reverse("api:commodity-list")
        self.detail_url_name = "api:commodity-detail"
        super().setUp()

    def test_create(self):
        data = {
            "name": fake.name()[:127],
            "code": fake.name()[:64],
            "description": fake.text(),
            "is_lab_commodity": random.choice([True, False]),
            "is_pharmacy_commodity": random.choice([True, False]),
            "organisation": self.global_organisation.pk,
        }
        response = self.client.post(self.url_list, data)
        assert response.status_code == 201, response.json()
        assert response.data["code"] == data["code"]

    def test_retrieve(self):
        instance = baker.make(
            Commodity,
            organisation=self.global_organisation,
        )
        response = self.client.get(self.url_list)
        assert response.status_code == 200, response.json()
        assert response.data["count"] >= 1, response.json()

        ids = [a["id"] for a in response.data["results"]]
        assert str(instance.pk) in ids

    def test_patch(self):
        instance = baker.make(
            Commodity,
            organisation=self.global_organisation,
        )
        edit = {"active": False}
        url = reverse(self.detail_url_name, kwargs={"pk": instance.pk})
        response = self.client.patch(url, edit)

        assert response.status_code == 200, response.json()
        assert response.data["active"] == edit["active"]

    def test_put(self):
        instance = baker.make(
            Commodity,
            organisation=self.global_organisation,
        )
        data = {
            "name": fake.name()[:127],
            "code": fake.name()[:64],
            "description": fake.text(),
            "is_lab_commodity": random.choice([True, False]),
            "is_pharmacy_commodity": random.choice([True, False]),
            "organisation": self.global_organisation.pk,
            "active": False,
        }
        url = reverse(self.detail_url_name, kwargs={"pk": instance.pk})
        response = self.client.put(url, data)

        assert response.status_code == 200, response.json()
        assert response.data["active"] == data["active"]


class CommodityFormTest(LoggedInMixin, TestCase):
    def test_create(self):
        data = {
            "name": fake.name()[:127],
            "code": fake.name()[:64],
            "description": fake.text(),
            "is_lab_commodity": random.choice([True, False]),
            "is_pharmacy_commodity": random.choice([True, False]),
            "organisation": self.global_organisation.pk,
        }
        response = self.client.post(reverse("ops:commodity_create"), data=data)
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_update(self):
        instance = baker.make(
            Commodity,
            organisation=self.global_organisation,
        )
        data = {
            "name": fake.name()[:127],
            "code": fake.name()[:64],
            "description": fake.text(),
            "is_lab_commodity": random.choice([True, False]),
            "is_pharmacy_commodity": random.choice([True, False]),
            "organisation": self.global_organisation.pk,
            "active": False,
        }
        response = self.client.post(
            reverse("ops:commodity_update", kwargs={"pk": instance.pk}), data=data
        )
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_delete(self):
        instance = baker.make(
            Commodity,
            organisation=self.global_organisation,
        )
        response = self.client.post(
            reverse("ops:commodity_delete", kwargs={"pk": instance.pk}),
        )
        self.assertEqual(
            response.status_code,
            302,
        )
