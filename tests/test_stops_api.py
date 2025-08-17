import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pytest
import respx
from httpx import Response

import config
from api.http_client import init_http_client, close_http_client
from planner.stops_api import get_today_stops
from planner.dtos import TaskDTO
from api.errors import ApiError, DataValidationError


@pytest.mark.asyncio
async def test_stops_api_success(
    respx_mock: respx.MockRouter, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(config, "STOPS_API_URL", "https://api.test/stops")
    await init_http_client()
    respx_mock.get("https://api.test/stops").mock(
        return_value=Response(
            200,
            json=[
                {
                    "id": "t1",
                    "kind": "pickup",
                    "location": {"lat": 0.0, "lon": 0.0},
                    "window": None,
                    "size": 1,
                }
            ],
        )
    )
    stops = await get_today_stops()
    assert isinstance(stops[0], TaskDTO)
    await close_http_client()


@pytest.mark.asyncio
async def test_stops_api_error(
    respx_mock: respx.MockRouter, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(config, "STOPS_API_URL", "https://api.test/stops")
    await init_http_client()
    respx_mock.get("https://api.test/stops").mock(return_value=Response(500))
    with pytest.raises(ApiError):
        await get_today_stops()
    await close_http_client()


@pytest.mark.asyncio
async def test_stops_api_malformed(
    respx_mock: respx.MockRouter, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(config, "STOPS_API_URL", "https://api.test/stops")
    await init_http_client()
    respx_mock.get("https://api.test/stops").mock(
        return_value=Response(200, text="not json")
    )
    with pytest.raises(DataValidationError):
        await get_today_stops()
    await close_http_client()
