import datetime
import os
import tempfile
import uuid
from random import randint
from unittest.mock import patch

import pytest
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
from django.test import TestCase
from django.utils import timezone
from faker import Faker
from model_bakery import baker
from PIL import Image

from pepfar_mle.common.models import (
    Facility,
    Organisation,
    OwnerlessAbstractBase,
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


def test_facility_string_representation():
    """Test common behavior of the abstract base model."""
    facility_name = fake.name()
    mfl_code = randint(1, 999_999)
    county = "47_NAIROBI_CITY"
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
    assert str(facility) == f"{facility_name} - {mfl_code} (47_NAIROBI_CITY)"


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
    county = "47_NAIROBI_CITY"
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

    assert ("the facility name should exceed 3 characters") in e.value.messages


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


class AuditAbstractBaseModelTest(TestCase):
    """Test for AuditAbstract."""

    def setUp(self):
        """Onset of testcase."""
        self.leo = timezone.now()
        self.jana = timezone.now() - datetime.timedelta(days=1)
        self.juzi = timezone.now() - datetime.timedelta(days=2)
        self.user_1 = baker.make(settings.AUTH_USER_MODEL)
        self.user_2 = baker.make(settings.AUTH_USER_MODEL)

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
