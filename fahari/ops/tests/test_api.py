import json
import random
from datetime import date
from os.path import join

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
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
    FacilityDevice,
    FacilityDeviceRequest,
    FacilityNetworkStatus,
    FacilitySystem,
    FacilitySystemTicket,
    SecurityIncidence,
    SiteMentorship,
    StockReceiptVerification,
    TimeSheet,
    UoM,
    UoMCategory,
    WeeklyProgramUpdate,
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
        self.pack_sizes = baker.make(UoM, 5, organisation=self.global_organisation)
        self.commodity = baker.make(
            Commodity,
            pack_sizes=self.pack_sizes,
            organisation=self.global_organisation,
        )
        super().setUp()

    def test_create(self):
        data = {
            "facility": self.facility.pk,
            "commodity": self.commodity.pk,
            "pack_size": self.pack_sizes[0].pk,
            "description": fake.text(),
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
            commodity=self.commodity,
            pack_size=self.pack_sizes[2],
            facility=self.facility,
            organisation=self.global_organisation,
        )
        data = {
            "facility": self.facility.pk,
            "description": fake.text(),
            "pack_size": self.pack_sizes[1].pk,
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
        self.pack_sizes = baker.make(UoM, 5, organisation=self.global_organisation)
        self.commodity = baker.make(
            Commodity,
            pack_sizes=self.pack_sizes,
            organisation=self.global_organisation,
        )
        super().setUp()

    def test_create(self):
        with open(
            join(settings.STATIC_ROOT, "images", "favicons", "android-icon-192x192.png"), "rb"
        ) as image_file:
            data = {
                "facility": self.facility.pk,
                "description": fake.text(),
                "pack_size": self.pack_sizes[0].pk,
                "delivery_note_number": fake.name()[:63],
                "quantity_received": "10.0",
                "batch_number": fake.name()[:63],
                "expiry_date": date.today().isoformat(),
                "delivery_date": date.today().isoformat(),
                "comments": fake.text(),
                "organisation": self.global_organisation.pk,
                "delivery_note_image": image_file,
                "commodity": self.commodity.pk,
                "active": False,
            }
            response = self.client.post(
                reverse("ops:stock_receipt_verification_create"), data=data
            )
            self.assertEqual(
                response.status_code,
                302,
            )

    def test_update(self):
        instance = baker.make(
            StockReceiptVerification,
            commodity=self.commodity,
            pack_size=self.pack_sizes[2],
            facility=self.facility,
            organisation=self.global_organisation,
        )
        with open(
            join(settings.STATIC_ROOT, "images", "favicons", "android-icon-192x192.png"), "rb"
        ) as image_file:
            data = {
                "pk": instance.pk,
                "facility": self.facility.pk,
                "description": fake.text(),
                "pack_size": self.pack_sizes[1].pk,
                "delivery_note_number": fake.name()[:63],
                "quantity_received": "10.0",
                "batch_number": fake.name()[:63],
                "expiry_date": date.today().isoformat(),
                "delivery_date": date.today().isoformat(),
                "comments": fake.text(),
                "organisation": self.global_organisation.pk,
                "delivery_note_image": image_file,
                "commodity": self.commodity.pk,
                "active": False,
            }
            response = self.client.post(
                reverse("ops:stock_receipt_verification_update", kwargs={"pk": instance.pk}),
                data=data,
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
            "notes": "-",
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
            "title": fake.text(),
            "attachment": SimpleUploadedFile(
                "some_file.txt", "some file contents go here...".encode()
            ),
            "attendees": json.dumps([fake.name(), fake.name()]),
            "organisation": self.global_organisation.pk,
            "description": "-",
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
            "title": fake.text(),
            "attachment": SimpleUploadedFile(
                "some_file.txt", "some file contents go here...".encode()
            ),
            "attendees": f"{fake.name()},{fake.name()}",
            "organisation": self.global_organisation.pk,
            "description": "-",
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
        self.pack_sizes = baker.make(UoM, 3, organisation=self.global_organisation)
        super().setUp()

    def test_create(self):
        data = {
            "name": fake.name()[:127],
            "code": fake.name()[:64],
            "pack_sizes": map(lambda p: p.pk, self.pack_sizes),
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
            pack_sizes=self.pack_sizes,
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
            pack_sizes=self.pack_sizes,
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
            pack_sizes=self.pack_sizes,
            organisation=self.global_organisation,
        )
        data = {
            "name": fake.name()[:127],
            "code": fake.name()[:64],
            "pack_sizes": map(lambda p: p.pk, self.pack_sizes),
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
        pack_sizes = baker.make(UoM, 5, organisation=self.global_organisation)
        data = {
            "name": fake.name()[:127],
            "code": fake.name()[:64],
            "pack_sizes": map(lambda p: p.pk, pack_sizes),
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
        pack_sizes = baker.make(UoM, 3, organisation=self.global_organisation)
        instance = baker.make(
            Commodity,
            pack_sizes=pack_sizes,
            organisation=self.global_organisation,
        )
        data = {
            "name": fake.name()[:127],
            "code": fake.name()[:64],
            "pack_sizes": map(lambda p: p.pk, instance.pack_sizes.all()),
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


class UoMFormTest(LoggedInMixin, TestCase):
    def test_create(self):
        uom_category = baker.make(UoMCategory, organisation=self.global_organisation)
        data = {"name": fake.name()[:127], "category": uom_category.pk}
        response = self.client.post(reverse("ops:uom_create"), data=data)
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_update(self):
        instance = baker.make(UoM, organisation=self.global_organisation)
        uom_category = baker.make(UoMCategory, organisation=self.global_organisation)
        data = {"name": fake.name()[:127], "category": uom_category.pk}
        response = self.client.post(
            reverse("ops:uom_update", kwargs={"pk": instance.pk}), data=data
        )
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_delete(self):
        instance = baker.make(UoM, organisation=self.global_organisation)
        response = self.client.post(
            reverse("ops:uom_delete", kwargs={"pk": instance.pk}),
        )
        self.assertEqual(
            response.status_code,
            302,
        )


class UoMCategoryFormTest(LoggedInMixin, TestCase):
    def test_create(self):
        data = {
            "name": fake.name()[:120],
            "measure_type": UoMCategory.MeasureTypes.UNIT.value,
            "organisation": self.global_organisation.pk,
        }
        response = self.client.post(reverse("ops:uom_category_create"), data=data)
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_update(self):
        instance = baker.make(UoMCategory, organisation=self.global_organisation)
        data = {
            "name": fake.name()[:120],
            "measure_type": UoMCategory.MeasureTypes.UNIT.value,
            "organisation": self.global_organisation.pk,
        }
        response = self.client.post(
            reverse("ops:uom_category_update", kwargs={"pk": instance.pk}), data=data
        )
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_delete(self):
        instance = baker.make(UoMCategory, organisation=self.global_organisation)
        response = self.client.post(
            reverse("ops:uom_category_delete", kwargs={"pk": instance.pk}),
        )
        self.assertEqual(
            response.status_code,
            302,
        )


class FacilityNetworkStatusViewsetTest(LoggedInMixin, APITestCase):
    def setUp(self):
        self.url_list = reverse("api:facilitynetworkstatus-list")
        self.facility = baker.make(Facility, organisation=self.global_organisation)
        super().setUp()

    def test_create(self):
        data = {
            "facility": self.facility.pk,
            "has_network": fake.pybool(),
            "has_internet": fake.pybool(),
        }
        response = self.client.post(self.url_list, data)
        assert response.status_code == 201, response.json()
        assert response.data["has_network"] == data["has_network"]
        assert response.data["has_internet"] == data["has_internet"]

    def test_retrieve(self):
        instance = baker.make(
            FacilityNetworkStatus,
            organisation=self.global_organisation,
            has_internet=fake.pybool(),
        )
        response = self.client.get(self.url_list)
        assert response.status_code == 200, response.json()
        assert response.data["count"] >= 1, response.json()

        internet_connections = [a["has_internet"] for a in response.data["results"]]
        assert instance.has_internet in internet_connections

    def test_patch(self):
        instance = baker.make(
            FacilityNetworkStatus, organisation=self.global_organisation, has_network=fake.pybool()
        )
        edit = {"has_network": fake.pybool()}
        url = reverse("api:facilitynetworkstatus-detail", kwargs={"pk": instance.pk})
        response = self.client.patch(url, edit)

        assert response.status_code == 200, response.json()
        assert response.data["has_network"] == edit["has_network"]

    def test_put(self):
        instance = baker.make(
            FacilityNetworkStatus,
            organisation=self.global_organisation,
        )
        data = {
            "facility": self.facility.pk,
            "organisation": self.global_organisation.pk,
            "has_network": fake.pybool(),
            "has_internet": fake.pybool(),
        }
        url = reverse("api:facilitynetworkstatus-detail", kwargs={"pk": instance.pk})
        response = self.client.put(url, data)

        assert response.status_code == 200, response.json()
        assert response.data["has_network"] == data["has_network"]
        assert response.data["has_internet"] == data["has_internet"]


class FacilityNetworkStatusFormTest(LoggedInMixin, TestCase):
    def setUp(self):
        self.user = baker.make(settings.AUTH_USER_MODEL, email=fake.email())
        self.facility = baker.make(
            Facility,
            is_fahari_facility=True,
            county=random.choice(WHITELIST_COUNTIES),
            operation_status="Operational",
            organisation=self.global_organisation,
        )
        super().setUp()

    def test_create(self):
        data = {
            "facility": self.facility.pk,
            "has_network": fake.pybool(),
            "has_internet": fake.pybool(),
        }
        response = self.client.post(reverse("ops:network_status_create"), data=data)
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_update(self):
        instance = baker.make(
            FacilityNetworkStatus,
            organisation=self.global_organisation,
        )
        data = {
            "pk": instance.pk,
            "facility": self.facility.pk,
            "has_network": fake.pybool(),
            "has_internet": fake.pybool(),
        }
        response = self.client.post(
            reverse("ops:network_status_update", kwargs={"pk": instance.pk}), data=data
        )
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_delete(self):
        instance = baker.make(
            FacilityNetworkStatus,
            organisation=self.global_organisation,
        )
        response = self.client.post(
            reverse("ops:network_status_delete", kwargs={"pk": instance.pk}),
        )
        self.assertEqual(
            response.status_code,
            302,
        )


class FacilityDeviceViewsetTest(LoggedInMixin, APITestCase):
    def setUp(self):
        self.url_list = reverse("api:facilitydevice-list")
        self.facility = baker.make(Facility, organisation=self.global_organisation)
        super().setUp()

    def test_create(self):
        data = {
            "facility": self.facility.pk,
            "number_of_devices": random.randint(1, 10),
            "number_of_ups": random.randint(1, 10),
            "server_specification": fake.text(),
        }
        response = self.client.post(self.url_list, data)
        assert response.status_code == 201, response.json()
        assert response.data["number_of_devices"] == data["number_of_devices"]
        assert response.data["number_of_ups"] == data["number_of_ups"]
        assert response.data["server_specification"] == data["server_specification"]

    def test_retrieve(self):
        instance = baker.make(
            FacilityDevice,
            organisation=self.global_organisation,
            number_of_ups=random.randint(1, 10),
        )
        response = self.client.get(self.url_list)
        assert response.status_code == 200, response.json()
        assert response.data["count"] >= 1, response.json()

        ups = [a["number_of_ups"] for a in response.data["results"]]
        assert instance.number_of_ups in ups

    def test_patch(self):
        instance = baker.make(
            FacilityDevice,
            organisation=self.global_organisation,
        )
        edit = {"number_of_devices": random.randint(1, 10)}
        url = reverse("api:facilitydevice-detail", kwargs={"pk": instance.pk})
        response = self.client.patch(url, edit)

        assert response.status_code == 200, response.json()
        assert response.data["number_of_devices"] == edit["number_of_devices"]

    def test_put(self):
        instance = baker.make(
            FacilityDevice,
            organisation=self.global_organisation,
        )
        data = {
            "facility": self.facility.pk,
            "organisation": self.global_organisation.pk,
            "number_of_devices": random.randint(1, 10),
            "number_of_ups": random.randint(1, 10),
            "server_specification": fake.text(),
        }
        url = reverse("api:facilitydevice-detail", kwargs={"pk": instance.pk})
        response = self.client.put(url, data)

        assert response.status_code == 200, response.json()
        assert response.data["number_of_devices"] == data["number_of_devices"]
        assert response.data["number_of_ups"] == data["number_of_ups"]
        assert response.data["server_specification"] == data["server_specification"]


class FacilityDeviceFormTest(LoggedInMixin, TestCase):
    def setUp(self):
        self.user = baker.make(settings.AUTH_USER_MODEL, email=fake.email())
        self.facility = baker.make(
            Facility,
            is_fahari_facility=True,
            county=random.choice(WHITELIST_COUNTIES),
            operation_status="Operational",
            organisation=self.global_organisation,
        )
        super().setUp()

    def test_create(self):
        data = {
            "facility": self.facility.pk,
            "number_of_devices": random.randint(1, 10),
            "number_of_ups": random.randint(1, 10),
            "server_specification": fake.text(),
        }
        response = self.client.post(reverse("ops:facility_device_create"), data=data)
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_update(self):
        instance = baker.make(
            FacilityDevice,
            organisation=self.global_organisation,
        )
        data = {
            "pk": instance.pk,
            "facility": self.facility.pk,
            "number_of_devices": random.randint(1, 10),
            "number_of_ups": random.randint(1, 10),
            "server_specification": fake.text(),
        }
        response = self.client.post(
            reverse("ops:facility_device_update", kwargs={"pk": instance.pk}), data=data
        )
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_delete(self):
        instance = baker.make(
            FacilityDevice,
            organisation=self.global_organisation,
        )
        response = self.client.post(
            reverse("ops:facility_device_delete", kwargs={"pk": instance.pk}),
        )
        self.assertEqual(
            response.status_code,
            302,
        )


class FacilityDeviceRequestViewsetTest(LoggedInMixin, APITestCase):
    def setUp(self):
        self.url_list = reverse("api:facilitydevicerequest-list")
        self.facility = baker.make(Facility, organisation=self.global_organisation)
        super().setUp()

    def test_create(self):
        data = {
            "facility": self.facility.pk,
            "device_requested": fake.text(max_nb_chars=50),
            "request_type": "NEW",
            "request_details": fake.text(),
            "date_requested": date.today().isoformat(),
            "delivery_date": date.today().isoformat(),
        }
        response = self.client.post(self.url_list, data)
        assert response.status_code == 201, response.json()
        assert response.data["device_requested"] == data["device_requested"]
        assert response.data["request_details"] == data["request_details"]

    def test_retrieve(self):
        instance = baker.make(
            FacilityDeviceRequest,
            organisation=self.global_organisation,
            device_requested=fake.text(max_nb_chars=50),
        )
        response = self.client.get(self.url_list)
        assert response.status_code == 200, response.json()
        assert response.data["count"] >= 1, response.json()

        devices = [a["device_requested"] for a in response.data["results"]]
        assert instance.device_requested in devices

    def test_patch(self):
        instance = baker.make(
            FacilityDeviceRequest,
            organisation=self.global_organisation,
            device_requested=fake.text(max_nb_chars=50),
        )
        edit = {"device_requested": fake.text(max_nb_chars=50)}
        url = reverse("api:facilitydevicerequest-detail", kwargs={"pk": instance.pk})
        response = self.client.patch(url, edit)

        assert response.status_code == 200, response.json()
        assert response.data["device_requested"] == edit["device_requested"]

    def test_put(self):
        instance = baker.make(
            FacilityDeviceRequest,
            organisation=self.global_organisation,
            device_requested=fake.text(max_nb_chars=50),
        )
        data = {
            "facility": self.facility.pk,
            "device_requested": fake.text(max_nb_chars=50),
            "request_type": "NEW",
            "request_details": fake.text(),
        }
        url = reverse("api:facilitydevicerequest-detail", kwargs={"pk": instance.pk})
        response = self.client.put(url, data)

        assert response.status_code == 200, response.json()
        assert response.data["device_requested"] == data["device_requested"]
        assert response.data["request_details"] == data["request_details"]


class FacilityDeviceRequestFormTest(LoggedInMixin, TestCase):
    def setUp(self):
        self.user = baker.make(settings.AUTH_USER_MODEL, email=fake.email())
        self.facility = baker.make(
            Facility,
            is_fahari_facility=True,
            county=random.choice(WHITELIST_COUNTIES),
            operation_status="Operational",
            organisation=self.global_organisation,
        )
        super().setUp()

    def test_create(self):
        data = {
            "facility": self.facility.pk,
            "device_requested": fake.text(max_nb_chars=50),
            "request_type": "NEW",
            "request_details": fake.text(),
        }
        response = self.client.post(reverse("ops:facility_device_request_create"), data=data)
        self.assertEqual(
            response.status_code,
            200,
        )

    def test_update(self):
        instance = baker.make(
            FacilityDeviceRequest,
            organisation=self.global_organisation,
            device_requested=fake.text(max_nb_chars=50),
            request_details=fake.text(),
        )
        data = {
            "pk": instance.pk,
            "facility": self.facility.pk,
            "device_requested": fake.text(max_nb_chars=50),
            "request_details": fake.text(),
        }
        response = self.client.post(
            reverse("ops:facility_device_request_update", kwargs={"pk": instance.pk}), data=data
        )
        self.assertEqual(
            response.status_code,
            200,
        )

    def test_delete(self):
        instance = baker.make(
            FacilityDeviceRequest,
            organisation=self.global_organisation,
            device_requested=fake.text(max_nb_chars=50),
        )
        response = self.client.post(
            reverse("ops:facility_device_request_delete", kwargs={"pk": instance.pk}),
        )
        self.assertEqual(
            response.status_code,
            302,
        )


class SecurityIncidenceViewsetTest(LoggedInMixin, APITestCase):
    def setUp(self):
        self.url_list = reverse("api:securityincidence-list")
        self.facility = baker.make(Facility, organisation=self.global_organisation)
        super().setUp()

    def test_create(self):
        data = {
            "facility": self.facility.pk,
            "title": fake.text(max_nb_chars=50),
            "details": fake.text(),
            "reported_on": date.today().isoformat(),
            "reported_by": self.user.pk,
        }
        response = self.client.post(self.url_list, data)
        assert response.status_code == 201, response.json()
        assert response.data["title"] == data["title"]
        assert response.data["details"] == data["details"]
        assert response.data["reported_on"] == data["reported_on"]
        assert response.data["reported_by"] == data["reported_by"]

    def test_retrieve(self):
        instance = baker.make(
            SecurityIncidence,
            organisation=self.global_organisation,
            title=fake.text(max_nb_chars=50),
        )
        response = self.client.get(self.url_list)
        assert response.status_code == 200, response.json()
        assert response.data["count"] >= 1, response.json()

        incidences = [a["title"] for a in response.data["results"]]
        assert instance.title in incidences

    def test_patch(self):
        instance = baker.make(
            SecurityIncidence,
            organisation=self.global_organisation,
            title=fake.text(max_nb_chars=50),
        )
        edit = {"title": fake.text(max_nb_chars=50)}
        url = reverse("api:securityincidence-detail", kwargs={"pk": instance.pk})
        response = self.client.patch(url, edit)

        assert response.status_code == 200, response.json()
        assert response.data["title"] == edit["title"]

    def test_put(self):
        instance = baker.make(
            SecurityIncidence,
            organisation=self.global_organisation,
            title=fake.text(max_nb_chars=50),
        )
        data = {
            "facility": self.facility.pk,
            "title": fake.text(max_nb_chars=50),
            "details": fake.text(),
            "reported_on": date.today().isoformat(),
            "reported_by": self.user.pk,
        }
        url = reverse("api:securityincidence-detail", kwargs={"pk": instance.pk})
        response = self.client.put(url, data)

        assert response.status_code == 200, response.json()
        assert response.data["title"] == data["title"]
        assert response.data["details"] == data["details"]
        assert response.data["reported_on"] == data["reported_on"]
        assert response.data["reported_by"] == data["reported_by"]


class SecurityIncidenceFormTest(LoggedInMixin, TestCase):
    def setUp(self):
        self.user = baker.make(settings.AUTH_USER_MODEL, email=fake.email())
        self.facility = baker.make(
            Facility,
            is_fahari_facility=True,
            county=random.choice(WHITELIST_COUNTIES),
            operation_status="Operational",
            organisation=self.global_organisation,
        )
        super().setUp()

    def test_create(self):
        data = {
            "facility": self.facility.pk,
            "title": fake.text(max_nb_chars=50),
            "details": fake.text(),
            "reported_on": date.today().isoformat(),
            "reported_by": self.user.pk,
        }
        response = self.client.post(reverse("ops:security_incidence_create"), data=data)
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_update(self):
        instance = baker.make(
            SecurityIncidence,
            title=fake.text(max_nb_chars=50),
            details=fake.text(),
        )
        data = {
            "pk": instance.pk,
            "facility": self.facility.pk,
            "title": fake.text(max_nb_chars=50),
            "details": fake.text(),
            "reported_on": date.today().isoformat(),
            "reported_by": self.user.pk,
        }
        response = self.client.post(
            reverse("ops:security_incidence_update", kwargs={"pk": instance.pk}), data=data
        )
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_delete(self):
        instance = baker.make(
            SecurityIncidence,
            organisation=self.global_organisation,
            title=fake.text(max_nb_chars=50),
        )
        response = self.client.post(
            reverse("ops:security_incidence_delete", kwargs={"pk": instance.pk}),
        )
        self.assertEqual(
            response.status_code,
            302,
        )
