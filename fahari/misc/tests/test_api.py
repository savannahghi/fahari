import json

from django.urls import reverse
from faker import Faker
from model_bakery import baker
from rest_framework import status

from fahari.common.models import Facility
from fahari.common.tests.test_api import LoggedInMixin
from fahari.ops.models import Commodity, UoM, UoMCategory

from ..models import SheetToDBMappingsMetadata, StockVerificationReceiptsAdapter

fake = Faker()


class TestGoogleSheetToDjangoModelAdapterMixin(LoggedInMixin):
    """Test the Google Sheets adapter mixin API."""

    def setUp(self) -> None:
        super().setUp()
        self.facilities = [
            baker.make(
                Facility,
                mfl_code=mfl_code,
                name=fake.name(),
                organisation=self.global_organisation,
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
            UoMCategory, measure_type="unit", name="unit", organisation=self.global_organisation
        )
        self.pack_sizes = [
            baker.make(
                UoM, category=self.unit, name=ps_name, organisation=self.global_organisation
            )
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
                organisation=self.global_organisation,
            ),
            baker.make(
                Commodity,
                code="DTG",
                name="Dolutegravir(DTG) 50mg tabs",
                pack_sizes=[self.pack_sizes[0]],
                organisation=self.global_organisation,
            ),
            baker.make(
                Commodity,
                code="AZT/3TC",
                name="Zidovudine/Lamivudine (AZT/3TC) FDC (300/150mg) Tablets",
                pack_sizes=[self.pack_sizes[1]],
                organisation=self.global_organisation,
            ),
        ]
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
            organisation=self.global_organisation,
        )
        self.svr_adapter = baker.make(
            StockVerificationReceiptsAdapter,
            county="Nairobi",
            data_sheet_name="Form Responses 1",
            field_mappings_meta=self.mappings_meta,
            last_column="M",
            organisation=self.global_organisation,
            sheet_id="1ATZKDHRQzZWNFQgFUMZ2yc_-R4TamfoK6jg--7KFTic",
        )

    def test_ingest_from_last_position(self) -> None:
        """Test `ingest_from_last_position` action."""

        url = reverse(
            "api:stockverificationreceiptsadapter-ingest-from-last-position",
            args=(self.svr_adapter.pk,),
        )
        response = self.client.post(url, data={})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["ingested_rows"] == 38  # noqa

    def test_ingest_from_last_position_failure(self) -> None:
        """Test ingesting failure."""

        self.commodities[2].delete()  # Delete a commodity to induce failure
        url = reverse(
            "api:stockverificationreceiptsadapter-ingest-from-last-position",
            args=(self.svr_adapter.pk,),
        )
        response = self.client.post(url, data={})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["row_index"] == 4  # noqa
