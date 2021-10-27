import json
from typing import List, Sequence

import pytest
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.db import models
from faker import Faker
from model_bakery import baker

from config.asgi import application as asgi_application
from fahari.common.models import Facility
from fahari.common.tests.test_api import global_organisation
from fahari.ops.models import Commodity, StockReceiptVerification, UoM, UoMCategory

from ..models import SheetToDBMappingsMetadata, StockVerificationReceiptsAdapter

fake = Faker()
pytestmark = pytest.mark.django_db


@pytest.fixture
async def get_svr_adapter_test_facilities() -> List[Facility]:  # noqa
    def make_facility(mfl_code: int) -> Facility:
        return baker.make(
            Facility, mfl_code=mfl_code, name=fake.name(), organisation=global_organisation()
        )

    facilities = [
        await database_sync_to_async(make_facility)(mfl_code)
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

    return facilities


@pytest.fixture
async def get_svr_adapter_test_pack_sizes() -> List[UoM]:  # noqa
    def make_unit() -> UoMCategory:
        return baker.make(
            UoMCategory, measure_type="unit", name="unit", organisation=global_organisation()
        )

    def make_pack_size(name, category_unit) -> UoM:
        return baker.make(
            UoM, category=category_unit, name=name, organisation=global_organisation()
        )

    unit = await database_sync_to_async(make_unit)()
    return [
        await database_sync_to_async(make_pack_size)(ps_name, unit)
        for ps_name in ("Packs of 30s", "Packs of 60s", "Packs of 90s")
    ]


@pytest.fixture
async def get_svr_adapter_test_commodities(get_svr_adapter_test_pack_sizes) -> List[Commodity]:
    pack_sizes = get_svr_adapter_test_pack_sizes

    def make_commodity(code: str, name: str, commodity_pack_sizes: Sequence[UoM]) -> Commodity:
        return baker.make(
            Commodity,
            code=code,
            name=name,
            pack_sizes=commodity_pack_sizes,
            organisation=global_organisation(),
        )

    return [
        await database_sync_to_async(make_commodity)(
            code="TDF/3TC/DTG",
            name=(
                "Tenofovir/Lamivudine/Dolutegravir (TDF/3TC/DTG) FDC (300/300/50mg) " "FDC Tablets"
            ),
            commodity_pack_sizes=[pack_sizes[2]],  # noqa
        ),
        await database_sync_to_async(make_commodity)(
            code="DTG",
            name="Dolutegravir(DTG) 50mg tabs",
            commodity_pack_sizes=[pack_sizes[0]],  # noqa
        ),
        await database_sync_to_async(make_commodity)(
            code="AZT/3TC",
            name="Zidovudine/Lamivudine (AZT/3TC) FDC (300/150mg) Tablets",
            commodity_pack_sizes=[pack_sizes[1]],  # noqa
        ),
    ]


@pytest.fixture
async def get_test_svr_mappings_metadata() -> SheetToDBMappingsMetadata:
    def make_mappings_metadata() -> SheetToDBMappingsMetadata:
        return baker.make(
            SheetToDBMappingsMetadata,
            name="Nairobi SVR Sheet to DB Mappings Metadata",
            mappings_metadata=json.load(
                open("data/nairobi_svr_sheet_to_db_mappings_metadata.json")
            ),
            version="1.0.0",
            organisation=global_organisation(),
        )

    return await database_sync_to_async(make_mappings_metadata)()


@pytest.fixture
async def get_test_svr_adapter_instance(
    get_test_svr_mappings_metadata,
) -> StockVerificationReceiptsAdapter:
    def make_svr_adapter() -> StockVerificationReceiptsAdapter:
        return baker.make(
            StockVerificationReceiptsAdapter,
            county="Nairobi",
            data_sheet_name="Form Responses 1",
            field_mappings_meta=get_test_svr_mappings_metadata,
            last_column="M",
            organisation=global_organisation(),
            sheet_id="1ATZKDHRQzZWNFQgFUMZ2yc_-R4TamfoK6jg--7KFTic",
        )

    return await database_sync_to_async(make_svr_adapter)()


@pytest.fixture
async def get_svr_consumer_authenticated_communicator(async_client) -> WebsocketCommunicator:
    user = await database_sync_to_async(_get_user)()
    await database_sync_to_async(lambda: async_client.force_login(user))()
    headers = [
        (b"origin", b"..."),
        (b"cookie", async_client.cookies.output(header="", sep="; ").encode()),
    ]
    return WebsocketCommunicator(
        asgi_application, "/ws/misc/stock_receipts_verification_ingest/", headers=headers
    )


@pytest.mark.asyncio
async def test_svr_adapter_consumer_connect(async_client) -> None:
    communicator = WebsocketCommunicator(
        asgi_application, "/ws/misc/stock_receipts_verification_ingest/"
    )
    connected, _ = await communicator.connect()

    assert not connected  # Connection should fail because the user is not authenticated

    user = await database_sync_to_async(_get_user)()
    await database_sync_to_async(lambda: async_client.force_login(user))()
    headers = [
        (b"origin", b"..."),
        (b"cookie", async_client.cookies.output(header="", sep="; ").encode()),
    ]
    authenticated_communicator = WebsocketCommunicator(
        asgi_application, "/ws/misc/stock_receipts_verification_ingest/", headers=headers
    )
    connected, _ = await authenticated_communicator.connect()

    assert connected  # This connection should be successful
    await authenticated_communicator.disconnect()


@pytest.mark.asyncio
async def test_svr_adapter_consumer_ingest_from_last_position(
    get_svr_adapter_test_facilities,
    get_svr_adapter_test_commodities,
    get_test_svr_adapter_instance,
    get_svr_consumer_authenticated_communicator,
    transactional_db,
) -> None:
    communicator: WebsocketCommunicator = get_svr_consumer_authenticated_communicator  # noqa

    assert not await database_sync_to_async(lambda: StockReceiptVerification.objects.exists())()
    await communicator.connect()
    await communicator.send_json_to({"adapter": str(get_test_svr_adapter_instance.pk)})  # noqa
    for index in range(1, 39):
        response = await communicator.receive_json_from(5 * 60)
        assert response["type"] == "progress"
        assert response["data"]["current"] == index
        assert response["data"]["total"] == 38

    success_response = await communicator.receive_json_from(5 * 60)
    assert success_response["type"] == "success"
    assert success_response["data"]["ingested_rows"] == 38
    assert await database_sync_to_async(lambda: StockReceiptVerification.objects.exists())()

    await communicator.disconnect()


@pytest.mark.asyncio
async def test_svr_adapter_consumer_ingest_from_last_position_failure(
    get_svr_adapter_test_facilities,
    get_svr_adapter_test_commodities,
    get_test_svr_adapter_instance,
    get_svr_consumer_authenticated_communicator,
    transactional_db,
) -> None:
    timeout = 60  # 1 minute
    commodities: Sequence[Commodity] = get_svr_adapter_test_commodities  # noqa
    communicator: WebsocketCommunicator = get_svr_consumer_authenticated_communicator  # noqa

    # Delete a commodity to induce failure
    await database_sync_to_async(lambda: commodities[2].delete())()

    await communicator.connect(timeout=timeout)
    await communicator.send_json_to({"adapter": str(get_test_svr_adapter_instance.pk)})  # noqa
    for index in range(1, 3):
        response = await communicator.receive_json_from(timeout=timeout)
        assert response["type"] == "progress"
        assert response["data"]["current"] == index
        assert response["data"]["total"] == 38

    error_response = await communicator.receive_json_from(timeout=timeout)
    assert error_response["type"] == "error"
    assert error_response["data"]["row_index"] == 4
    assert not await database_sync_to_async(lambda: StockReceiptVerification.objects.exists())()

    await communicator.disconnect()


def _get_user() -> models.Model:
    return baker.make(
        get_user_model(), name=fake.name(), organisation=global_organisation(), is_superuser=True
    )
