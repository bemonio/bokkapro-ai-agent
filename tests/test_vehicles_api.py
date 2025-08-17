import pytest
import pytest_asyncio
import respx
from collections.abc import AsyncGenerator
from httpx import Response
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import config
from api.http_client import init_http_client, close_http_client
from api.vehicles import get_vehicles
from api.dtos import VehicleDTO
from api.errors import ApiError, DataValidationError


@pytest_asyncio.fixture(autouse=True)
async def _client(monkeypatch: pytest.MonkeyPatch) -> AsyncGenerator[None, None]:
    monkeypatch.setattr(config, "BOKKA_API_BASE_URL", "https://api.test")
    monkeypatch.setattr(config, "HTTP_RETRY_BACKOFF_SECONDS", 0.0)
    await init_http_client()
    yield
    await close_http_client()


@pytest.mark.asyncio
async def test_get_vehicles_success(respx_mock: respx.MockRouter) -> None:
    respx_mock.get("https://api.test/api/v1/vehicles").mock(
        return_value=Response(
            200,
            json=[
                {
                    "id": "1",
                    "plate": "A",
                    "capacity": 2,
                    "office": "HQ",
                    "division": None,
                }
            ],
        )
    )
    result = await get_vehicles()
    assert result == [
        VehicleDTO(id="1", plate="A", capacity=2, office="HQ", division=None)
    ]


@pytest.mark.asyncio
async def test_get_vehicles_api_error(respx_mock: respx.MockRouter) -> None:
    respx_mock.get("https://api.test/api/v1/vehicles").mock(
        return_value=Response(500, text="err")
    )
    with pytest.raises(ApiError):
        await get_vehicles()


@pytest.mark.asyncio
async def test_get_vehicles_retry_429(respx_mock: respx.MockRouter) -> None:
    respx_mock.get("https://api.test/api/v1/vehicles").mock(
        side_effect=[Response(429), Response(429), Response(429)]
    )
    with pytest.raises(ApiError):
        await get_vehicles()
    assert respx_mock.calls.call_count == config.HTTP_RETRY_ATTEMPTS


@pytest.mark.asyncio
async def test_get_vehicles_malformed_json(respx_mock: respx.MockRouter) -> None:
    respx_mock.get("https://api.test/api/v1/vehicles").mock(
        return_value=Response(200, text="notjson")
    )
    with pytest.raises(DataValidationError):
        await get_vehicles()
