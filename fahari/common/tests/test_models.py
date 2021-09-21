import datetime
import os
import tempfile
import uuid
from random import randint
from unittest.mock import patch

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files import File
from django.test import TestCase
from django.utils import timezone
from faker import Faker
from model_bakery import baker
from PIL import Image

from fahari.common.models import (
    Facility,
    Organisation,
    OwnerlessAbstractBase,
    System,
    UserFacilityAllotment,
    is_image_type,
    unique_list,
)

fake = Faker()

pytestmark = pytest.mark.django_db

CURRENT_FOLDER = os.path.dirname(__file__)


def test_unique_list():
    """Test for getting the unique list."""
    lst = [1, 2, 2, 3]
    unique = unique_list(lst)
    assert unique == [1, 2, 3]


def test_is_image_type():
    assert is_image_type("image/png") is True
    assert is_image_type("image/jpeg") is True
    assert is_image_type("application/pdf") is False


def test_system_string_representation():
    system_name = fake.name()
    system = baker.make(System, name=system_name)
    assert str(system) == system_name


def test_facility_string_representation():
    """Test common behavior of the abstract base model."""
    facility_name = fake.name()
    mfl_code = randint(1, 999_999)
    county = "Nairobi"
    created_by = uuid.uuid4()
    updated_by = created_by
    organisation = baker.make("common.Organisation")

    facility = Facility(
        name=facility_name,
        mfl_code=mfl_code,
        county=county,
        organisation=organisation,
        created_by=created_by,
        updated_by=updated_by,
    )
    facility.save()
    assert str(facility) == f"{facility_name} - {mfl_code} (Nairobi)"


def test_google_application_credentials():
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    assert cred_path != ""
    assert os.path.exists(cred_path)
    assert os.path.isfile(cred_path)


def test_facility_attachment_string_representation():
    """Test common behavior of the abstract base model."""
    org = baker.make(Organisation)
    facility = baker.make("common.Facility", name="Test Facility", organisation=org)
    notes = "Notes"
    facility_attachment = baker.make(
        "common.FacilityAttachment",
        facility=facility,
        notes=notes,
        title="Title",
        organisation=org,
        content_type="text/plain",
        _create_files=True,
    )
    assert str(facility_attachment) == "Title"


def get_temporary_image(temp_file):
    size = (200, 200)
    color = (255, 0, 0, 0)
    image = Image.new("RGB", size, color)
    image.save(temp_file, "jpeg")
    return temp_file


def test_facility_attachment_inconsistent_organisation():
    org1 = baker.make(Organisation)
    org2 = baker.make(Organisation)
    facility = baker.make("common.Facility", name="Test Facility", organisation=org1)
    notes = "Notes"
    temp_file = tempfile.NamedTemporaryFile()
    test_image = get_temporary_image(temp_file)
    facility_attachment = baker.prepare(
        "common.FacilityAttachment",
        facility=facility,
        notes=notes,
        title="Title",
        organisation=org2,
        data=test_image.file,
        content_type="image/jpeg",
    )
    with pytest.raises(ValidationError) as e:
        facility_attachment.save()

    assert (
        "'The organisation provided is not consistent with that of "
        "organisation fields in related resources" in str(e.value.messages)
    )


def test_facility_attachment_blank_organisation():
    org1 = baker.make(Organisation)
    facility = baker.make("common.Facility", name="Test Facility", organisation=org1)
    notes = "Notes"
    temp_file = tempfile.NamedTemporaryFile()
    test_image = get_temporary_image(temp_file)
    facility_attachment = baker.prepare(
        "common.FacilityAttachment",
        facility=facility,
        notes=notes,
        title="Title",
        organisation=None,
        data=test_image.name,
    )
    with pytest.raises(Organisation.DoesNotExist):
        facility_attachment.save()


def test_facility_attachment_non_image_type():
    org = baker.make(Organisation)
    facility = baker.make("common.Facility", name="Test Facility", organisation=org)
    notes = "Notes"
    temp_file = tempfile.NamedTemporaryFile()
    test_image = get_temporary_image(temp_file)
    facility_attachment = baker.prepare(
        "common.FacilityAttachment",
        facility=facility,
        notes=notes,
        title="Title",
        organisation=org,
        data=File(test_image.file),
        content_type="application/pdf",  # will not trigger validation
    )
    facility_attachment.save()


def test_facility_attachment_excessively_tall_image():
    org = baker.make(Organisation)
    facility = baker.make("common.Facility", name="Test Facility", organisation=org)
    notes = "Notes"

    overly_tall = os.path.join(CURRENT_FOLDER, "overly_tall_image.png")
    with open(overly_tall, "rb") as test_image:
        fieldfile = File(test_image)
        facility_attachment = baker.prepare(
            "common.FacilityAttachment",
            facility=facility,
            notes=notes,
            title="Title",
            organisation=org,
            data=fieldfile,
            content_type="image/png",
        )
        with pytest.raises(ValidationError) as e:
            facility_attachment.save()

        assert "larger than allowable dimension" in str(e.value.messages)


def test_facility_attachment_excessively_wide_image():
    org = baker.make(Organisation)
    facility = baker.make("common.Facility", name="Test Facility", organisation=org)
    notes = "Notes"

    overly_wide = os.path.join(CURRENT_FOLDER, "overly_wide_image.png")
    with open(overly_wide, "rb") as test_image:
        fieldfile = File(test_image)
        facility_attachment = baker.prepare(
            "common.FacilityAttachment",
            facility=facility,
            notes=notes,
            title="Title",
            organisation=org,
            data=fieldfile,
            content_type="image/png",
        )
        with pytest.raises(ValidationError) as e:
            facility_attachment.save()

        assert "larger than allowable dimension" in str(e.value.messages)


def test_facility_error_saving():
    """Test common behavior of the abstract base model."""
    facility_name = "a"  # too short, will trigger validator
    mfl_code = randint(1, 999_999)
    county = "Nairobi"
    created_by = uuid.uuid4()
    updated_by = created_by
    organisation = baker.make("common.Organisation")

    facility = Facility(
        name=facility_name,
        mfl_code=mfl_code,
        county=county,
        organisation=organisation,
        created_by=created_by,
        updated_by=updated_by,
    )
    with pytest.raises(ValidationError) as e:
        facility.save()

    assert "the facility name should exceed 3 characters" in e.value.messages


def test_facility_invalid_constituency_selection():
    facility = Facility(
        name="ABC Hospital",
        mfl_code=123456,
        county="Kajiado",
        organisation=baker.make("common.Organisation"),
        constituency="Westlands",  # doesn't belong in Kajiado county
    )
    with pytest.raises(ValidationError) as e:
        facility.save()

    assert '"Westlands" constituency does not belong to "Kajiado" county' in e.value.messages


def test_facility_invalid_sub_county_selection():
    facility = Facility(
        name="XYZ Medical Center",
        mfl_code=123456,
        county="Nairobi",
        organisation=baker.make("common.Organisation"),
        sub_county="Kajiado East",  # doesn't belong in Nairobi county
    )
    with pytest.raises(ValidationError) as e:
        facility.save()

    assert '"Kajiado East" sub county does not belong to "Nairobi" county' in e.value.messages


def test_facility_invalid_ward_selection():
    facility = Facility(
        name="ABC Hospital",
        mfl_code=123456,
        county="Kajiado",
        organisation=baker.make("common.Organisation"),
        sub_county="Kajiado Central",
        ward="Ngando",
    )
    with pytest.raises(ValidationError) as e:
        facility.save()

    assert '"Ngando" ward does not belong to "Kajiado Central" sub county' in e.value.messages


def test_facility_ward_selection_without_sub_county_selection():
    facility = Facility(
        name="XYZ VCT Clinic",
        mfl_code=123456,
        county="Nairobi",
        organisation=baker.make("common.Organisation"),
        ward="Ngara",  # missing sub county selection
    )
    with pytest.raises(ValidationError) as e:
        facility.save()

    assert 'The sub county in which "Ngara" ward belongs to must be provided' in e.value.messages


def test_organisation_string_representation():
    org = baker.make("common.Organisation", organisation_name="Test Organisation")
    assert str(org) == "Test Organisation"


class DictError(OwnerlessAbstractBase):
    """Raise validation errors with a dict."""

    class Meta:
        """Define app name for the model."""

        app_label = "dict_error"

    model_validators = [
        "validation_one",
        "validation_two",
        "validation_three",
        "validation_four",
        "validation_one",  # duplicate
    ]

    def validation_one(self):
        """Define first validation raise with a dictionary."""
        raise ValidationError({"field_1": "Error!", "field_2": "Error!"})

    def validation_two(self):
        """Define second validation raise with a dictionary."""
        raise ValidationError({"field_1": "Error2!"})

    def validation_three(self):
        """Define third validation raise with a message."""
        raise ValidationError("plain error")

    def validation_four(self):
        """Define fourth validation raise with a list of messages."""
        raise ValidationError(["list error one", "list error two"])


def test_run_model_validators():
    """Test model validation."""
    instance = DictError()
    with pytest.raises(ValidationError) as e:
        instance.run_model_validators()

    assert e.value.message_dict == {
        "field_1": ["Error!", "Error2!"],
        "field_2": ["Error!"],
        "__all__": ["plain error", "list error one", "list error two"],
    }


def test_duplicate_validator_ignored():
    """Test same validator not run twice on a model."""
    instance = DictError()
    with patch.object(instance, "validation_one") as validation_one:
        with pytest.raises(ValidationError):
            instance.run_model_validators()

    validation_one.assert_called_once_with()


def test_abstract_base_manager_get_active():
    """Tests for AbstractBaseManager."""
    organisation = baker.make(Organisation)
    baker.make(Facility, 10, active=True, organisation=organisation)
    baker.make(Facility, 5, active=False, organisation=organisation)

    assert Facility.objects.count() == 15
    assert Facility.objects.active().count() == 10
    assert Facility.objects.non_active().count() == 5


class AuditAbstractBaseModelTest(TestCase):
    """Test for AuditAbstract."""

    def setUp(self):
        """Onset of testcase."""
        self.leo = timezone.now()
        self.jana = timezone.now() - datetime.timedelta(days=1)
        self.juzi = timezone.now() - datetime.timedelta(days=2)
        self.user_1 = baker.make(settings.AUTH_USER_MODEL, email=fake.email())
        self.user_2 = baker.make(settings.AUTH_USER_MODEL, email=fake.email())

    def test_validate_updated_date_greater_than_created(self):
        """Test that updated date is greater than created."""
        fake = Facility(created=self.leo, updated=self.jana)
        error_msg = "The updated date cannot be less than the created date"

        with pytest.raises(ValidationError) as ve:
            fake.validate_updated_date_greater_than_created()
        assert error_msg in ve.value.messages

    def test_preserve_created_and_created_by(self):
        """Test for preserve and created by."""
        # Create  a new instance
        fake = baker.make(
            Facility,
            created=self.jana,
            updated=self.leo,
            created_by=self.user_1.pk,
            updated_by=self.user_1.pk,
        )
        # Switch the create
        fake.created = self.juzi
        fake.save()

        assert self.jana == fake.created

        # Switch created_by
        fake.created_by = self.user_2.pk
        fake.updated_by = self.user_2.pk
        fake.save()

        assert self.user_1.pk == fake.created_by
        assert self.user_2.pk == fake.updated_by

    def test_preserve_created_and_created_by_org(self):
        """Test for preserve crated and created by org."""
        # Create  a new instance
        fake = baker.make(
            Organisation,
            created=self.jana,
            updated=self.leo,
            created_by=self.user_1.pk,
            updated_by=self.user_1.pk,
        )
        # Switch the create
        fake.created = self.juzi
        fake.save()

        assert self.jana == fake.created

        # Switch created_by
        fake.created_by = self.user_2.pk
        fake.updated_by = self.user_2.pk
        fake.save()

        assert self.user_1.pk == fake.created_by
        assert self.user_2.pk == fake.updated_by

    def test_timezone(self):
        """Test for timezone."""
        naive_datetime = timezone.now() + datetime.timedelta(500)
        with pytest.raises(ValidationError) as e:
            baker.make(Facility, created=naive_datetime)

        expected = "The updated date cannot be less than the created date"
        assert expected in e.value.messages

        instance = baker.make(Facility)
        naive_after_object_is_saved = datetime.datetime.now()
        instance.updated = naive_after_object_is_saved
        instance.save()
        instance.refresh_from_db()
        assert timezone.is_aware(instance.updated)

        # Test that we don't need to make created timezone aware
        # It is already timezone aware
        assert timezone.is_aware(instance.created)
        created_naive_datetime = datetime.datetime.now()
        instance.create = created_naive_datetime  # This should not even update
        instance.save()
        assert timezone.is_aware(instance.created)

    def test_owner(self):
        """Test for test owner."""
        org = baker.make(Organisation, organisation_name="Savannah Informatics")
        fake = baker.make(
            Facility,
            created=self.jana,
            updated=self.leo,
            created_by=self.user_1.pk,
            updated_by=self.user_1.pk,
            organisation=org,
        )
        fake.save()

        assert fake.organisation.org_code == fake.owner


class LinkedRecordsBaseTest(TestCase):
    """Tests for the `LinkedRecordsBase` model and it's associated manager and queryset."""

    def setUp(self) -> None:
        super(LinkedRecordsBaseTest, self).setUp()
        # Since `LinkedRecordsBase` is an abstract class, we use one of it's
        # concrete descendants for the tests.
        from fahari.ops.models import FacilitySystem

        self.organisation = baker.make(Organisation)
        self.facilities = baker.make(
            Facility,
            5,
            county="Kajiado",
            sub_county="Kajiado East",
            organisation=self.organisation,
        )
        self.systems = baker.make(System, 5, organisation=self.organisation)
        self.user = baker.make(get_user_model(), name=fake.name(), organisation=self.organisation)
        self.user_facility_allotment: UserFacilityAllotment = baker.make(
            UserFacilityAllotment,
            allotment_type=UserFacilityAllotment.AllotmentType.BY_FACILITY.value,
            facilities=self.facilities,
            organisation=self.organisation,
            user=self.user,
        )
        self.linked_instance: FacilitySystem = baker.make(
            FacilitySystem,
            facility=self.facilities[0],
            organisation=self.organisation,
            previous_node=None,
            system=self.systems[0],
            version="1.0.0",
        )

    def test_create_root_node(self):
        """Test that creation of root nodes works as expected."""

        from fahari.ops.models import FacilitySystem

        data = {
            "facility": self.facilities[1],
            "organisation": self.organisation,
            "system": self.systems[1],
            "version": "1.0.0",
        }
        root_node: FacilitySystem = FacilitySystem.objects.create_root_node(**data)

        assert root_node is not None
        assert root_node.is_root_node
        assert root_node.previous_node is None
        assert root_node in FacilitySystem.root_nodes()

    def test_create_leaf_node(self):
        """Test that creation of leaf nodes works as expected."""

        from fahari.ops.models import FacilitySystem

        data = {
            "facility": self.facilities[0],
            "organisation": self.organisation,
            "system": self.systems[0],
            "version": "2.0.0",
        }
        leaf_node: FacilitySystem = FacilitySystem.objects.create_leaf_node(**data)

        assert leaf_node is not None
        assert leaf_node.is_leaf_node
        assert leaf_node.next_node is None
        assert leaf_node.previous_node == self.linked_instance
        assert self.linked_instance.next_node == leaf_node
        assert FacilitySystem.nodes(**data).count() == 2
        assert leaf_node in FacilitySystem.leaf_nodes()

        data["version"] = "2.1.0"
        leaf_node1: FacilitySystem = FacilitySystem.objects.create_leaf_node(**data)
        leaf_node.refresh_from_db()

        assert leaf_node1.next_node is None
        assert leaf_node1.is_leaf_node
        assert leaf_node1.previous_node == leaf_node
        assert not leaf_node.is_leaf_node
        assert leaf_node.next_node == leaf_node1
        assert leaf_node.previous_node == self.linked_instance
        assert self.linked_instance.next_node == leaf_node
        assert FacilitySystem.nodes(**data).count() == 3
        assert leaf_node not in FacilitySystem.leaf_nodes()
        assert leaf_node1 in FacilitySystem.leaf_nodes()

    def test_create_leaf_node_of_a_non_existing_link(self):
        """Assert that creating a leaf node of a non existing link leads to a new link."""

        from fahari.ops.models import FacilitySystem

        data = {
            "facility": self.facilities[1],
            "organisation": self.organisation,
            "system": self.systems[1],
            "version": "1.0.0",
        }
        leaf_node: FacilitySystem = FacilitySystem.objects.create_leaf_node(**data)

        assert leaf_node is not None
        assert leaf_node.is_root_node
        assert leaf_node.next_node is None
        assert leaf_node.previous_node is None
        assert FacilitySystem.nodes(**data).count() == 1
        assert FacilitySystem.root_nodes().count() == 2
        assert leaf_node in FacilitySystem.root_nodes()

    def test_delete(self):
        ...

    def test_leaf_node_methods(self):
        """"""
        ...

    def test_leaf_nodes_methods(self):
        ...

    def test_nodes_methods(self):
        ...

    def test_root_node_methods(self):
        ...

    def test_root_nodes_methods(self):
        ...


class UserFacilityAllotmentTest(TestCase):
    """Tests for the UserFacilityAllotment model."""

    def setUp(self) -> None:
        super().setUp()
        self.by_both = UserFacilityAllotment.AllotmentType.BY_FACILITY_AND_REGION
        self.by_facility = UserFacilityAllotment.AllotmentType.BY_FACILITY
        self.by_region = UserFacilityAllotment.AllotmentType.BY_REGION
        self.organisation = baker.make(Organisation)
        self.facilities = baker.make(
            Facility,
            5,
            county="Kajiado",
            sub_county="Kajiado East",
            organisation=self.organisation,
        )
        self.user = baker.make(get_user_model(), name=fake.name(), organisation=self.organisation)
        self.user_facility_allotment: UserFacilityAllotment = baker.make(
            UserFacilityAllotment,
            allotment_type=UserFacilityAllotment.AllotmentType.BY_FACILITY.value,
            facilities=self.facilities,
            organisation=self.organisation,
            user=self.user,
        )

    def test_constituency_must_be_provided_if_region_type_is_constituency(self):
        """Test that at least 1 constituency must be provided when region type is constituency."""

        constituency = UserFacilityAllotment.RegionType.CONSTITUENCY
        with pytest.raises(ValidationError) as e1:
            baker.make(
                UserFacilityAllotment,
                allotment_type=self.by_both.value,
                region_type=constituency.value,
            )

        with pytest.raises(ValidationError) as e2:
            baker.make(
                UserFacilityAllotment,
                allotment_type=self.by_region.value,
                region_type=constituency.value,
            )

        assert (
            'At least 1 constituency must be selected if region type is "%s"' % constituency.label
            in e1.value.messages
        )
        assert (
            'At least 1 constituency must be selected if region type is "%s"' % constituency.label
            in e2.value.messages
        )

    def test_county_must_be_provided_if_region_type_is_county(self):
        """Test that at least 1 county must be provided when region type is county."""

        county = UserFacilityAllotment.RegionType.COUNTY
        with pytest.raises(ValidationError) as e1:
            baker.make(
                UserFacilityAllotment, allotment_type=self.by_both.value, region_type=county.value
            )

        with pytest.raises(ValidationError) as e2:
            baker.make(
                UserFacilityAllotment,
                allotment_type=self.by_region.value,
                region_type=county.value,
            )

        assert (
            'At least 1 county must be selected if region type is "%s"' % county.label
            in e1.value.messages
        )
        assert (
            'At least 1 county must be selected if region type is "%s"' % county.label
            in e2.value.messages
        )

    def test_sub_county_must_be_provided_if_region_type_is_sub_county(self):
        """Test that at least 1 sub_county must be provided when region type is sub sub_county."""

        sub_county = UserFacilityAllotment.RegionType.SUB_COUNTY
        with pytest.raises(ValidationError) as e1:
            baker.make(
                UserFacilityAllotment,
                allotment_type=self.by_both.value,
                region_type=sub_county.value,
            )

        with pytest.raises(ValidationError) as e2:
            baker.make(
                UserFacilityAllotment,
                allotment_type=self.by_region.value,
                region_type=sub_county.value,
            )

        assert (
            'At least 1 sub_county must be selected if region type is "%s"' % sub_county.label
            in e1.value.messages
        )
        assert (
            'At least 1 sub_county must be selected if region type is "%s"' % sub_county.label
            in e2.value.messages
        )

    def test_ward_must_be_provided_if_region_type_is_ward(self):
        """Test that at least 1 ward must be provided when region type is ward."""

        ward = UserFacilityAllotment.RegionType.WARD
        with pytest.raises(ValidationError) as e1:
            baker.make(
                UserFacilityAllotment, allotment_type=self.by_both.value, region_type=ward.value
            )

        with pytest.raises(ValidationError) as e2:
            baker.make(
                UserFacilityAllotment,
                allotment_type=self.by_region.value,
                region_type=ward.value,
            )

        assert (
            'At least 1 ward must be selected if region type is "%s"' % ward.label
            in e1.value.messages
        )
        assert (
            'At least 1 ward must be selected if region type is "%s"' % ward.label
            in e2.value.messages
        )

    def test_get_absolute_url(self):
        """Test the `self.get_absolute_url` method."""

        allotment = self.user_facility_allotment
        assert (
            allotment.get_absolute_url()
            == "/common/user_facility_allotment_update/%s" % allotment.pk
        )

    def test_get_facilities_for_user(self):
        """Tests for the `UserFacilityAllotment.get_facilities_for_user()` method."""

        user = baker.make(get_user_model(), name=fake.name(), organisation=self.organisation)

        assert UserFacilityAllotment.get_facilities_for_user(user).count() == 0
        assert UserFacilityAllotment.get_facilities_for_user(self.user).count() == len(
            self.facilities
        )

    def test_region_type_must_be_provided_if_allot_by_region_or_both(self):
        """Test that a region type must be provided when allotment type is by region or both."""

        with pytest.raises(ValidationError) as e1:
            baker.make(UserFacilityAllotment, allotment_type=self.by_both.value, region_type=None)

        with pytest.raises(ValidationError) as e2:
            baker.make(
                UserFacilityAllotment,
                allotment_type=self.by_region.value,
                region_type=None,
            )

        assert (
            'A region type must be provided if allotment type is "%s"' % self.by_both.label
            in e1.value.messages
        )
        assert (
            'A region type must be provided if allotment type is "%s"' % self.by_region.label
            in e2.value.messages
        )

    def test_representation(self):
        """Test the `self.__str__()` method."""

        assert str(self.user_facility_allotment) == "User: %s; Allotment Type: %s" % (
            self.user_facility_allotment.user.name,
            self.user_facility_allotment.get_allotment_type_display(),
        )

    def test_user_facility_allotment_by_both_facility_and_region(self):
        """Test that a user can be allotted facilities by both region and facility."""

        baker.make(
            Facility,
            20,
            county="Kajiado",
            constituency="Kajiado West",
            organisation=self.organisation,
            sub_county="Kajiado West",
            ward="Magadi",
        )
        baker.make(
            Facility,
            30,
            county="Nairobi",
            constituency="Starehe",
            organisation=self.organisation,
            sub_county="Starehe",
            ward="Ngara",
        )
        user = baker.make(get_user_model(), name=fake.name(), organisation=self.organisation)
        allotment: UserFacilityAllotment = baker.make(
            UserFacilityAllotment,
            allotment_type=self.by_both.value,
            facilities=self.facilities,
            organisation=self.organisation,
            region_type=UserFacilityAllotment.RegionType.WARD.value,
            wards=["Magadi"],
            user=user,
        )

        assert allotment
        assert allotment.allotment_type == self.by_both.value
        assert UserFacilityAllotment.get_facilities_for_allotment(allotment).count() == 25

        allotment.wards = ["Magadi", "Ngara"]
        allotment.save()

        assert UserFacilityAllotment.get_facilities_for_allotment(allotment).count() == 55

    def test_user_facility_allotment_by_facility(self):
        """Test that a user can be allotted individual facilities."""

        facilities = baker.make(Facility, 20, organisation=self.organisation)
        user = baker.make(get_user_model(), name=fake.name(), organisation=self.organisation)
        allotment: UserFacilityAllotment = baker.make(
            UserFacilityAllotment,
            allotment_type=UserFacilityAllotment.AllotmentType.BY_FACILITY.value,
            facilities=facilities[10:],
            organisation=self.organisation,
            region_type=UserFacilityAllotment.RegionType.SUB_COUNTY.value,
            sub_counties=["Kajiado East"],  # This should not affect the allotted facilities count
            user=user,
        )

        assert allotment
        assert allotment.allotment_type == UserFacilityAllotment.AllotmentType.BY_FACILITY.value
        assert UserFacilityAllotment.get_facilities_for_allotment(allotment).count() == 10

        allotment.region_type = None
        allotment.save()

        assert UserFacilityAllotment.get_facilities_for_allotment(allotment).count() == 10

    def test_user_facility_allotment_by_county(self):
        """Test that a user can be allotted facilities by county."""

        baker.make(Facility, 25, county="Nairobi", organisation=self.organisation)
        user = baker.make(get_user_model(), name=fake.name(), organisation=self.organisation)
        allotment: UserFacilityAllotment = baker.make(
            UserFacilityAllotment,
            allotment_type=UserFacilityAllotment.AllotmentType.BY_REGION.value,
            counties=["Nairobi"],
            facilities=self.facilities,  # This should not affect the allotted facilities count
            organisation=self.organisation,
            region_type=UserFacilityAllotment.RegionType.COUNTY.value,
            user=user,
        )

        assert allotment
        assert allotment.allotment_type == UserFacilityAllotment.AllotmentType.BY_REGION.value
        assert UserFacilityAllotment.get_facilities_for_allotment(allotment).count() == 25

        allotment.counties = ["Nairobi", "Kajiado"]
        allotment.save()

        # After this, the allotment should have 25 facilities in Nairobi and 5 in Kajiado.
        # The 5 facilities from Kajiado are created during this fixture setup, i.e check the
        # `self.setup()` method.
        assert UserFacilityAllotment.get_facilities_for_user(allotment.user).count() == 30

    def test_user_facility_allotment_by_constituency(self):
        """Test that a user can be allotted facilities by constituency."""

        baker.make(
            Facility,
            25,
            county="Nairobi",
            constituency="Westlands",
            organisation=self.organisation,
            sub_county="Westlands",
            ward="Kangemi",
        )
        baker.make(
            Facility,
            15,
            county="Nairobi",
            constituency="Dagoretti North",
            organisation=self.organisation,
            sub_county="Dagoretti North",
            ward="Gatini",
        )
        user = baker.make(get_user_model(), name=fake.name(), organisation=self.organisation)
        allotment: UserFacilityAllotment = baker.make(
            UserFacilityAllotment,
            allotment_type=UserFacilityAllotment.AllotmentType.BY_REGION.value,
            constituencies=["Westlands"],
            facilities=self.facilities,  # This should not affect the allotted facilities count
            organisation=self.organisation,
            region_type=UserFacilityAllotment.RegionType.CONSTITUENCY.value,
            user=user,
        )

        assert allotment
        assert allotment.allotment_type == UserFacilityAllotment.AllotmentType.BY_REGION.value
        assert UserFacilityAllotment.get_facilities_for_allotment(allotment).count() == 25

        allotment.constituencies = ["Dagoretti North", "Westlands"]
        allotment.save()

        assert UserFacilityAllotment.get_facilities_for_allotment(allotment).count() == 40

    def test_user_facility_allotment_by_sub_county(self):
        """Test that a user can be allotted facilities by sub county."""

        baker.make(
            Facility, 15, county="Nairobi", sub_county="Kamukunji", organisation=self.organisation
        )
        baker.make(
            Facility, 20, county="Kajiado", sub_county="Loitokitok", organisation=self.organisation
        )
        user = baker.make(get_user_model(), name=fake.name(), organisation=self.organisation)
        allotment: UserFacilityAllotment = baker.make(
            UserFacilityAllotment,
            allotment_type=UserFacilityAllotment.AllotmentType.BY_REGION.value,
            facilities=self.facilities,  # This should not affect the allotted facilities count
            organisation=self.organisation,
            region_type=UserFacilityAllotment.RegionType.SUB_COUNTY.value,
            sub_counties=["Kamukunji"],
            user=user,
        )

        assert allotment
        assert allotment.allotment_type == UserFacilityAllotment.AllotmentType.BY_REGION.value
        assert UserFacilityAllotment.get_facilities_for_allotment(allotment).count() == 15

        allotment.sub_counties = ["Kamukunji", "Loitokitok"]
        allotment.save()

        assert UserFacilityAllotment.get_facilities_for_allotment(allotment).count() == 35

    def test_user_facility_allotment_by_ward(self):
        """Test that a user can be allotted facilities by ward."""

        baker.make(
            Facility,
            20,
            county="Kajiado",
            constituency="Kajiado West",
            organisation=self.organisation,
            sub_county="Kajiado West",
            ward="Magadi",
        )
        baker.make(
            Facility,
            30,
            county="Nairobi",
            constituency="Starehe",
            organisation=self.organisation,
            sub_county="Starehe",
            ward="Ngara",
        )
        user = baker.make(get_user_model(), name=fake.name(), organisation=self.organisation)
        allotment: UserFacilityAllotment = baker.make(
            UserFacilityAllotment,
            allotment_type=UserFacilityAllotment.AllotmentType.BY_REGION.value,
            facilities=self.facilities,  # This should not affect the allotted facilities count
            organisation=self.organisation,
            region_type=UserFacilityAllotment.RegionType.WARD.value,
            wards=["Magadi"],
            user=user,
        )

        assert allotment
        assert allotment.allotment_type == UserFacilityAllotment.AllotmentType.BY_REGION.value
        assert UserFacilityAllotment.get_facilities_for_allotment(allotment).count() == 20

        allotment.wards = ["Magadi", "Ngara"]
        allotment.save()

        assert UserFacilityAllotment.get_facilities_for_allotment(allotment).count() == 50
