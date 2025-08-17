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
from api.crews import get_crews
from api.dtos import CrewDTO, CrewMemberDTO, VehicleDTO
from api.errors import ApiError, DataValidationError


@pytest_asyncio.fixture(autouse=True)
async def _client(monkeypatch: pytest.MonkeyPatch) -> AsyncGenerator[None, None]:
    monkeypatch.setattr(config, "BOKKA_API_BASE_URL", "https://api.test")
    monkeypatch.setattr(config, "HTTP_RETRY_BACKOFF_SECONDS", 0.0)
    await init_http_client()
    yield
    await close_http_client()


def _sample_payload() -> list[dict[str, object]]:
    return [
        {
            "id": "c1",
            "driver": {"id": "d1", "name": "D", "role": "driver"},
            "assistant": {"id": "a1", "name": "A", "role": "assistant"},
            "assistant2": None,
            "vehicle": {
                "id": "v1",
                "plate": "P",
                "capacity": 2,
                "office": "HQ",
                "division": None,
            },
            "office": "HQ",
            "division": None,
        }
    ]


@pytest.mark.asyncio
async def test_get_crews_success(respx_mock: respx.MockRouter) -> None:
    respx_mock.get("https://api.test/api/v1/crews").mock(
        return_value=Response(200, json=_sample_payload())
    )
    result = await get_crews()
    expected = [
        CrewDTO(
            id="c1",
            driver=CrewMemberDTO(id="d1", name="D", role="driver"),
            assistant=CrewMemberDTO(id="a1", name="A", role="assistant"),
            assistant2=None,
            vehicle=VehicleDTO(
                id="v1", plate="P", capacity=2, office="HQ", division=None
            ),
            office="HQ",
            division=None,
        )
    ]
    assert result == expected


@pytest.mark.asyncio
async def test_get_crews_api_error(respx_mock: respx.MockRouter) -> None:
    respx_mock.get("https://api.test/api/v1/crews").mock(
        return_value=Response(500, text="err")
    )
    with pytest.raises(ApiError):
        await get_crews()


@pytest.mark.asyncio
async def test_get_crews_retry_429(respx_mock: respx.MockRouter) -> None:
    respx_mock.get("https://api.test/api/v1/crews").mock(
        side_effect=[Response(429), Response(429), Response(429)]
    )
    with pytest.raises(ApiError):
        await get_crews()
    assert respx_mock.calls.call_count == config.HTTP_RETRY_ATTEMPTS


@pytest.mark.asyncio
async def test_get_crews_malformed_json(respx_mock: respx.MockRouter) -> None:
    respx_mock.get("https://api.test/api/v1/crews").mock(
        return_value=Response(200, text="bad")
    )
    with pytest.raises(DataValidationError):
        await get_crews()
