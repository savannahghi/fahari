import json

import pytest
from django.contrib.auth import get_user_model
from django.test.testcases import TestCase
from faker import Faker
from model_bakery import baker

from fahari.common.models import Facility, Organisation
from fahari.ops.models import Commodity, UoM, UoMCategory

from ..exceptions import ProcessGoogleSheetRowError
from ..models import SheetToDBMappingsMetadata, StockVerificationReceiptsAdapter

fake = Faker()


class SheetToDBMappingsMetadataTest(TestCase):
    """Tests for the `SheetToDBMappingsMetadata` model."""

    def setUp(self) -> None:
        super().setUp()
        self.organisation = baker.make(Organisation)
        self.mappings_meta = baker.make(
            SheetToDBMappingsMetadata,
            name="Nairobi SVR Sheet to DB Mappings Metadata",
            mappings_metadata=json.load(
                open("data/nairobi_svr_sheet_to_db_mappings_metadata.json")
            ),
            version="1.0.0",
            organisation=self.organisation,
        )
        self.mappings_meta_other = baker.make(
            SheetToDBMappingsMetadata,
            name="Nairobi SVR Sheet to DB Mappings Metadata",
            mappings_metadata=json.load(
                open("data/nairobi_svr_sheet_to_db_mappings_metadata.json")
            ),
            organisation=self.organisation,
        )

    def test_representation(self) -> None:
        """Test the `self.__str__()` method."""

        assert str(self.mappings_meta) == "Nairobi SVR Sheet to DB Mappings Metadata v1.0.0"
        assert str(self.mappings_meta_other) == "Nairobi SVR Sheet to DB Mappings Metadata"


class TestSheetVerificationReceiptsAdapter(TestCase):
    """Tests for the `StockVerificationReceiptsAdapter` model."""

    def setUp(self) -> None:
        super().setUp()
        self.organisation = baker.make(Organisation)
        self.facilities = [
            baker.make(
                Facility, mfl_code=mfl_code, name=fake.name(), organisation=self.organisation
            )
            for mfl_code in {
                13080,
                13173,
                12978,
                13218,
                13101,
                13258,
                17683,
                13009,
                13093,
                13121,
                19311,
                12935,
                13086,
                13210,
                13165,
                13173,
                23385,
                13062,
                13117,
                17683,
                18463,
                13188,
            }
        ]
        self.unit = baker.make(
            UoMCategory, measure_type="unit", name="unit", organisation=self.organisation
        )
        self.pack_sizes = [
            baker.make(UoM, category=self.unit, name=ps_name, organisation=self.organisation)
            for ps_name in ("Packs of 30s", "Packs of 60s", "Packs of 90s")
        ]
        self.commodities = [
            baker.make(
                Commodity,
                code="TDF/3TC/DTG",
                name=(
                    "Tenofovir/Lamivudine/Dolutegravir (TDF/3TC/DTG) FDC (300/300/50mg) "
                    "FDC Tablets"
                ),
                pack_sizes=[self.pack_sizes[2]],
                organisation=self.organisation,
            ),
            baker.make(
                Commodity,
                code="DTG",
                name="Dolutegravir(DTG) 50mg tabs",
                pack_sizes=[self.pack_sizes[0]],
                organisation=self.organisation,
            ),
            baker.make(
                Commodity,
                code="AZT/3TC",
                name="Zidovudine/Lamivudine (AZT/3TC) FDC (300/150mg) Tablets",
                pack_sizes=[self.pack_sizes[1]],
                organisation=self.organisation,
            ),
        ]
        self.user = baker.make(get_user_model(), name=fake.name(), organisation=self.organisation)
        self.ingest_context = {
            "extra_kwargs": {
                "created_by": self.user.pk,
                "organisation": self.user.organisation,  # noqa
                "updated_by": self.user.pk,
            }
        }
        self.mappings_meta = baker.make(
            SheetToDBMappingsMetadata,
            name="Nairobi SVR Sheet to DB Mappings Metadata",
            mappings_metadata=json.load(
                open("data/nairobi_svr_sheet_to_db_mappings_metadata.json")
            ),
            version="1.0.0",
            organisation=self.organisation,
        )
        self.svr_adapter = baker.make(
            StockVerificationReceiptsAdapter,
            county="Nairobi",
            data_sheet_name="Form Responses 1",
            field_mappings_meta=self.mappings_meta,
            last_column="M",
            organisation=self.organisation,
            sheet_id="1ATZKDHRQzZWNFQgFUMZ2yc_-R4TamfoK6jg--7KFTic",
        )

    def test_ingest_from_last_position(self) -> None:
        """Test the `self.__ingest_from_last_position()` method."""

        ingested = self.svr_adapter.ingest_from_last_position(None, **self.ingest_context)
        assert ingested == 38
        assert self.svr_adapter.position == 39
        assert self.svr_adapter.last_ingested is not None

    def test_ingest_from_last_position_failure(self) -> None:
        """Test ingesting failure."""

        self.commodities[2].delete()  # Delete a commodity to induce failure
        with pytest.raises(ProcessGoogleSheetRowError) as exp:
            self.svr_adapter.ingest_from_last_position(None, **self.ingest_context)

        assert exp.value.row_index == 4

    def test_representation(self) -> None:
        """Test the `self.__str__()` method."""

        assert str(self.svr_adapter) == "Nairobi"
