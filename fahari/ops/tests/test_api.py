import random

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from faker import Faker
from model_bakery import baker
from rest_framework.test import APITestCase

from fahari.common.constants import WHITELIST_COUNTIES
from fahari.common.models import Facility, System
from fahari.common.tests.test_api import LoggedInMixin
from fahari.ops.models import FacilitySystem, FacilitySystemTicket

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
        self.facility = baker.make(
            Facility,
            is_fahari_facility=True,
            county=random.choice(WHITELIST_COUNTIES),
            operation_status="Operational",
            organisation=self.global_organisation,
        )
        self.system = baker.make(System, organisation=self.global_organisation)
        super().setUp()

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
            302,
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
        print(response.content)
        self.assertEqual(
            response.status_code,
            302,
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
