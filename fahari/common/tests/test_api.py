"""Test for the common views."""
import random
import shutil
import uuid
from functools import partial
from os import path

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from faker import Faker
from model_bakery import baker
from model_bakery.recipe import Recipe
from rest_framework import status
from rest_framework.test import APITestCase

from fahari.common.constants import WHITELIST_COUNTIES
from fahari.common.models import Facility, Organisation, System, UserFacilityAllotment

from .test_utils import patch_baker

DIR_PATH = path.join(path.dirname(path.abspath(__file__)))
MEDIA_PATH = path.join(DIR_PATH, "media")

http_origin_header = {"HTTP_ORIGIN": "http://sil.com"}
fake = Faker()


def delete_media_file():
    """Delete the media folder after tests."""
    if path.exists(MEDIA_PATH):
        shutil.rmtree(MEDIA_PATH)


def global_organisation():
    """Create organisation for running test."""
    org_id = "ebef581c-494b-4772-9e49-0b0755c44e61"
    code = 50
    organisation_name = "Demo Hospital"
    try:
        return Organisation.objects.get(
            id=org_id,
            code=code,
            organisation_name=organisation_name,
        )
    except Organisation.DoesNotExist:
        return baker.make(
            Organisation,
            id=org_id,
            organisation_name=organisation_name,
            code=code,
        )


class LoggedInMixin(APITestCase):
    """Define a logged in session for use in tests."""

    def setUp(self):
        """Create a test user for the logged in session."""
        super(LoggedInMixin, self).setUp()
        username = str(uuid.uuid4())
        self.user = get_user_model().objects.create_superuser(
            email=fake.email(),
            password="pass123",
            username=username,
        )
        all_perms = Permission.objects.all()
        for perm in all_perms:
            self.user.user_permissions.add(perm)
        self.user.organisation = self.global_organisation
        self.user.save()

        # Allot the given users to all the facilities in FYJ counties
        self.user_facility_allotment = baker.make(
            UserFacilityAllotment,
            allotment_type=UserFacilityAllotment.AllotmentType.BY_REGION.value,
            counties=WHITELIST_COUNTIES,
            organisation=self.global_organisation,
            region_type=UserFacilityAllotment.RegionType.COUNTY.value,
            user=self.user,
        )

        assert self.client.login(username=username, password="pass123") is True

        self.patch_organisation = partial(
            patch_baker, values={"organisation": self.global_organisation}
        )
        self.org_patcher = self.patch_organisation()
        self.org_patcher.start()
        self.addCleanup(self.org_patcher.stop)

        headers = self.extra_headers()
        self.client.get = partial(self.client.get, **headers)
        self.client.patch = partial(self.client.patch, **headers)
        self.client.post = partial(self.client.post, **headers)

    @property
    def global_organisation(self):
        """Create test organisation for the user."""
        return global_organisation()

    def make_recipe(self, model, **kwargs):
        """Ensure test user part of an organisation."""
        if "organisation" not in kwargs:
            kwargs["organisation"] = self.user.organisation
        return Recipe(model, **kwargs)

    def extra_headers(self):
        """Return an empty headers list."""
        return {}


class DRFSerializerExcelIOMixinTest(LoggedInMixin, APITestCase):
    """Test suite for excel io mixin API."""

    def setUp(self) -> None:
        super().setUp()
        from fahari.ops.models import FacilitySystem
        from fahari.ops.serializers import FacilitySystemSerializer

        versions = baker.make(FacilitySystem, 10, organisation=self.global_organisation)
        self.data = FacilitySystemSerializer(versions, many=True).data

    def test_dump_data(self) -> None:
        """Test `dump_data` action."""

        url = reverse("api:facilitysystem-dump-data")
        data = {"dump_fields": ["facility_data::name", "system_data::name", "version"]}
        response = self.client.get(url, data=data)

        assert response.status_code == status.HTTP_200_OK
        assert response["content-disposition"] == "attachment; filename=facility systems.xlsx"
        assert response["content-type"] == "application/xlsx; charset=utf-8"

    def test_get_available_fields(self) -> None:
        """Test the `get_available_fields` action."""

        url = reverse("api:facilitysystem-get-available-fields")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK, response.json()
        assert len(response.data) == 1
        assert response.data[0]["id"] == "*"

    def test_get_filter_form(self) -> None:
        """Test the `get_filter_form` action."""

        url = reverse("api:facilitysystem-get-filter-form")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response["content-type"] == "text/html; charset=utf-8"


class FacilityViewsetTest(LoggedInMixin, APITestCase):
    """Test suite for facilities API."""

    def setUp(self):
        self.url_list = reverse("api:facility-list")
        super().setUp()

    def test_create_facility(self):
        """Test add facility."""
        data = {
            "name": fake.name(),
            "mfl_code": random.randint(1, 999_999_999),
            "county": random.choice(WHITELIST_COUNTIES),
            "is_fahari_facility": True,
            "operation_status": "Operational",
            "organisation": self.global_organisation.pk,
        }

        response = self.client.post(self.url_list, data)
        assert response.status_code == 201, response.json()
        assert response.data["mfl_code"] == data["mfl_code"]

    def test_create_facility_no_organisation(self):
        """Test add facility."""
        data = {
            "name": fake.name(),
            "mfl_code": random.randint(1, 999_999_999),
            "county": random.choice(WHITELIST_COUNTIES),
            "is_fahari_facility": True,
            "operation_status": "Operational",
            # the user's organisation is used
        }

        response = self.client.post(self.url_list, data)
        assert response.status_code == 201, response.json()
        assert response.data["mfl_code"] == data["mfl_code"]

    def test_create_facility_error_supplied_id(self):
        """Test add facility."""
        data = {
            "id": uuid.uuid4(),
            "name": fake.name(),
            "mfl_code": random.randint(1, 999_999_999),
            "county": random.choice(WHITELIST_COUNTIES),
            "is_fahari_facility": True,
            "operation_status": "Operational",
            "organisation": self.global_organisation.pk,
        }

        response = self.client.post(self.url_list, data)
        assert response.status_code == 400, response.json()
        assert (
            "You are not allowed to pass object with an id" in response.json()["id"]
        ), response.json()

    def test_create_facility_error_bad_organisation(self):
        """Test add facility."""
        data = {
            "name": fake.name(),
            "mfl_code": random.randint(1, 999_999_999),
            "county": random.choice(WHITELIST_COUNTIES),
            "is_fahari_facility": True,
            "operation_status": "Operational",
            "organisation": uuid.uuid4(),  # does not exist
        }

        response = self.client.post(self.url_list, data)
        assert response.status_code == 400, response.json()
        assert "Ensure the organisation provided exists." in response.json()["organisation"]

    def test_retrieve_facility(self):
        """Test retrieving facility."""
        facility = baker.make(
            Facility,
            is_fahari_facility=True,
            county=random.choice(WHITELIST_COUNTIES),
            operation_status="Operational",
            organisation=self.global_organisation,
        )

        response = self.client.get(self.url_list)
        assert response.status_code == 200, response.json()
        assert response.data["count"] >= 1, response.json()

        facility_codes = [a["mfl_code"] for a in response.data["results"]]
        assert facility.mfl_code in facility_codes

    def test_retrieve_facility_with_fields(self):
        """Test retrieving facility."""
        facility = baker.make(
            Facility,
            is_fahari_facility=True,
            county=random.choice(WHITELIST_COUNTIES),
            operation_status="Operational",
            organisation=self.global_organisation,
        )

        # updated and other audit fields are popped and not returned
        url = f"{self.url_list}?fields=id,name,mfl_code,"
        "updated,created,updated_by,created_by,organisation"
        response = self.client.get(url)
        assert response.status_code == 200, response.json()
        assert response.data["count"] >= 1, response.json()

        facility_codes = [a["mfl_code"] for a in response.data["results"]]
        assert facility.mfl_code in facility_codes

    def test_retrieve_facility_with_combobox(self):
        """Test retrieving facility."""
        facility = baker.make(
            Facility,
            is_fahari_facility=True,
            county=random.choice(WHITELIST_COUNTIES),
            operation_status="Operational",
            organisation=self.global_organisation,
        )

        url = f"{self.url_list}?combobox={facility.pk}"
        response = self.client.get(url)
        assert response.status_code == 200, response.json()
        assert response.data["count"] >= 1, response.json()

        facility_codes = [a["mfl_code"] for a in response.data["results"]]
        assert facility.mfl_code in facility_codes

    def test_retrieve_facility_active(self):
        """Test retrieving facility."""
        facility = baker.make(
            Facility,
            is_fahari_facility=True,
            county=random.choice(WHITELIST_COUNTIES),
            operation_status="Operational",
            organisation=self.global_organisation,
        )

        url = f"{self.url_list}?active=True"
        response = self.client.get(url)
        assert response.status_code == 200, response.json()
        assert response.data["count"] >= 1, response.json()

        facility_codes = [a["mfl_code"] for a in response.data["results"]]
        assert facility.mfl_code in facility_codes

    def test_patch_facility(self):
        """Test changing user facility."""
        facility = baker.make(
            Facility,
            is_fahari_facility=True,
            county=random.choice(WHITELIST_COUNTIES),
            organisation=self.global_organisation,
        )

        edit_code = {"mfl_code": 999999999}
        url = reverse("api:facility-detail", kwargs={"pk": facility.pk})
        response = self.client.patch(url, edit_code)

        assert response.status_code == 200, response.json()
        assert response.data["mfl_code"] == edit_code["mfl_code"]

    def test_put_facility(self):
        """Test changing user and add new facility."""
        facility = baker.make(
            Facility,
            is_fahari_facility=True,
            county=random.choice(WHITELIST_COUNTIES),
            organisation=self.global_organisation,
        )
        data = {
            "name": fake.name(),
            "mfl_code": random.randint(1, 999_999_999),
            "county": random.choice(WHITELIST_COUNTIES),
            "is_fahari_facility": True,
            "operation_status": "Operational",
            "organisation": self.global_organisation.pk,
        }

        url = reverse("api:facility-detail", kwargs={"pk": facility.pk})
        response = self.client.put(url, data)

        assert response.status_code == 200, response.json()
        assert response.data["mfl_code"] == data["mfl_code"]


class FacilityFormTest(LoggedInMixin, TestCase):
    def test_create(self):
        data = {
            "name": fake.name(),
            "mfl_code": random.randint(1, 999_999_999),
            "county": random.choice(WHITELIST_COUNTIES),
            "is_fahari_facility": True,
            "operation_status": "Operational",
            "lon": 0.0,
            "lat": 0.0,
            "organisation": self.global_organisation.pk,
        }
        response = self.client.post(reverse("common:facility_create"), data=data)
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_update(self):
        facility = baker.make(
            Facility,
            is_fahari_facility=True,
            county=random.choice(WHITELIST_COUNTIES),
            organisation=self.global_organisation,
        )
        data = {
            "pk": facility.pk,
            "name": fake.name(),
            "mfl_code": random.randint(1, 999_999_999),
            "county": random.choice(WHITELIST_COUNTIES),
            "is_fahari_facility": True,
            "operation_status": "Operational",
            "lon": 0.0,
            "lat": 0.0,
            "organisation": self.global_organisation.pk,
        }
        response = self.client.post(
            reverse("common:facility_update", kwargs={"pk": facility.pk}), data=data
        )
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_delete(self):
        facility = baker.make(
            Facility,
            is_fahari_facility=True,
            county=random.choice(WHITELIST_COUNTIES),
            organisation=self.global_organisation,
        )
        response = self.client.post(
            reverse("common:facility_delete", kwargs={"pk": facility.pk}),
        )
        self.assertEqual(
            response.status_code,
            302,
        )


class SystemViewsetTest(LoggedInMixin, APITestCase):
    """Test suite for systems API."""

    def setUp(self):
        self.url_list = reverse("api:system-list")
        super().setUp()

    def test_create(self):
        data = {
            "name": fake.name()[:127],
            "description": fake.text(),
            "organisation": self.global_organisation.pk,
        }
        response = self.client.post(self.url_list, data)
        assert response.status_code == 201, response.json()
        assert response.data["name"] == data["name"]

    def test_retrieve_systems(self):
        system = baker.make(
            System,
            name=fake.name()[:127],
            organisation=self.global_organisation,
        )

        response = self.client.get(self.url_list)
        assert response.status_code == 200, response.json()
        assert response.data["count"] >= 1, response.json()

        names = [a["name"] for a in response.data["results"]]
        assert system.name in names

    def test_patch_system(self):
        system = baker.make(
            System,
            name=fake.name()[:127],
            organisation=self.global_organisation,
        )

        edit_name = {"name": fake.name()[:127]}
        url = reverse("api:system-detail", kwargs={"pk": system.pk})
        response = self.client.patch(url, edit_name)

        assert response.status_code == 200, response.json()
        assert response.data["name"] == edit_name["name"]

    def test_put_system(self):
        system = baker.make(
            System,
            name=fake.name()[:127],
            organisation=self.global_organisation,
        )
        data = {
            "name": fake.name()[:127],
            "description": fake.text(),
            "organisation": self.global_organisation.pk,
        }
        url = reverse("api:system-detail", kwargs={"pk": system.pk})
        response = self.client.put(url, data)

        assert response.status_code == 200, response.json()
        assert response.data["name"] == data["name"]


class SystemFormTest(LoggedInMixin, TestCase):
    def test_create(self):
        data = {
            "name": fake.name()[:127],
            "pattern": System.SystemPatters.HYBRID.value,
            "description": fake.text(),
            "organisation": self.global_organisation.pk,
        }
        response = self.client.post(reverse("common:system_create"), data=data)
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_update(self):
        system = baker.make(
            System,
            name=fake.name()[:127],
            organisation=self.global_organisation,
        )
        data = {
            "pk": system.pk,
            "name": fake.name()[:127],
            "pattern": System.SystemPatters.POINT_OF_CARE.value,
            "description": fake.text(),
            "organisation": self.global_organisation.pk,
        }
        response = self.client.post(
            reverse("common:system_update", kwargs={"pk": system.pk}), data=data
        )
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_delete(self):
        system = baker.make(
            System,
            name=fake.name()[:127],
            organisation=self.global_organisation,
        )
        response = self.client.post(
            reverse("common:system_delete", kwargs={"pk": system.pk}),
        )
        self.assertEqual(
            response.status_code,
            302,
        )


class UserFacilityViewSetTest(LoggedInMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.by_both = UserFacilityAllotment.AllotmentType.BY_FACILITY_AND_REGION
        self.by_facility = UserFacilityAllotment.AllotmentType.BY_FACILITY
        self.by_region = UserFacilityAllotment.AllotmentType.BY_REGION
        self.facilities = baker.make(
            Facility,
            20,
            is_fahari_facility=True,
            county="Nairobi",
            organisation=self.global_organisation,
        )

    def test_create(self):
        user = baker.make(get_user_model(), organisation=self.global_organisation)
        data = {
            "allotment_type": self.by_facility.value,
            "facilities": map(lambda f: f.pk, self.facilities),
            "user": user.pk,
            "organisation": self.global_organisation.pk,
        }
        response = self.client.post(reverse("api:userfacilityallotment-list"), data=data)
        assert response.status_code == 201

    def test_retrieve(self):
        user = baker.make(get_user_model(), organisation=self.global_organisation)
        instance: UserFacilityAllotment = baker.make(
            UserFacilityAllotment,
            allotment_type=self.by_facility.value,
            facilities=self.facilities,
            organisation=self.global_organisation,
            user=user,
        )

        response = self.client.get(reverse("api:userfacilityallotment-list"))
        assert response.status_code == 200, response.json()
        assert response.data["count"] >= 1, response.json()

        allotments = [entry["id"] for entry in response.data["results"]]
        assert str(instance.pk) in allotments

    def test_patch(self):
        user = baker.make(get_user_model(), organisation=self.global_organisation)
        instance: UserFacilityAllotment = baker.make(
            UserFacilityAllotment,
            allotment_type=self.by_facility.value,
            facilities=self.facilities,
            organisation=self.global_organisation,
            user=user,
        )

        data = {
            "allotment_type": self.by_region.value,
            "region_type": UserFacilityAllotment.RegionType.COUNTY.value,
            "counties": ["Nairobi"],
        }
        response = self.client.patch(
            reverse("api:userfacilityallotment-detail", kwargs={"pk": instance.pk}), data
        )
        assert response.status_code == 200, response.json()
        assert response.data["allotment_type"] == data["allotment_type"]
        assert response.data["region_type"] == data["region_type"]
        assert response.data["counties"] == data["counties"]

    def test_put(self):
        user = baker.make(get_user_model(), organisation=self.global_organisation)
        instance: UserFacilityAllotment = baker.make(
            UserFacilityAllotment,
            allotment_type=self.by_facility.value,
            facilities=self.facilities,
            organisation=self.global_organisation,
            user=user,
        )

        data = {
            "active": False,
            "allotment_type": self.by_region.value,
            "counties": ["Nairobi"],
            "organisation": self.global_organisation.pk,
            "region_type": UserFacilityAllotment.RegionType.COUNTY.value,
            "user": user.pk,
        }
        response = self.client.put(
            reverse("api:userfacilityallotment-detail", kwargs={"pk": instance.pk}), data
        )
        assert response.status_code == 200, response.json()
        assert response.data["active"] == data["active"]
        assert response.data["allotment_type"] == data["allotment_type"]
        assert response.data["region_type"] == data["region_type"]
        assert response.data["counties"] == data["counties"]


class UserFacilityAllotmentFormTest(LoggedInMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.by_both = UserFacilityAllotment.AllotmentType.BY_FACILITY_AND_REGION
        self.by_facility = UserFacilityAllotment.AllotmentType.BY_FACILITY
        self.by_region = UserFacilityAllotment.AllotmentType.BY_REGION
        self.facilities = baker.make(
            Facility,
            20,
            is_fahari_facility=True,
            county="Nairobi",
            organisation=self.global_organisation,
        )

    def test_create(self):
        user = baker.make(get_user_model(), organisation=self.global_organisation)
        data = {
            "allotment_type": self.by_facility.value,
            "facilities": map(lambda f: f.pk, self.facilities),
            "user": user.pk,
            "organisation": self.global_organisation.pk,
        }
        response = self.client.post(reverse("common:user_facility_allotment_create"), data=data)
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_update(self):
        instance = self.user_facility_allotment
        data = {
            "pk": instance.pk,
            "allotment_type": self.by_facility.value,
            "facilities": map(lambda f: f.pk, self.facilities),
            "user": self.user.pk,
            "organisation": self.global_organisation.pk,
            "active": False,
        }
        response = self.client.post(
            reverse("common:user_facility_allotment_update", kwargs={"pk": instance.pk}), data=data
        )
        self.assertEqual(
            response.status_code,
            302,
        )

    def test_delete(self):
        user = baker.make(get_user_model(), organisation=self.global_organisation)
        instance: UserFacilityAllotment = baker.make(
            UserFacilityAllotment,
            allotment_type=self.by_facility.value,
            facilities=self.facilities,
            organisation=self.global_organisation,
            user=user,
        )
        response = self.client.post(
            reverse("common:user_facility_allotment_delete", kwargs={"pk": instance.pk}),
        )
        self.assertEqual(
            response.status_code,
            302,
        )
