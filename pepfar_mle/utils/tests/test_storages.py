import pytest
from django.core.management import call_command
from model_bakery import baker

pytestmark = pytest.mark.django_db


class TestStorages:
    def test_static_root_google_cloud_storage(self):
        call_command("collectstatic", "--noinput")

    def test_media_root_google_cloud_storage(self):
        org = baker.make("common.Organisation")
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
        assert facility_attachment.data is not None
        assert facility_attachment.data.storage is not None
        assert facility_attachment.data.size > 0
