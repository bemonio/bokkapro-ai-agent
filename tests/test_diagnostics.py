import pytest
import respx
from httpx import AsyncClient, Response, ASGITransport
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import config
from main import app
from api.http_client import init_http_client, close_http_client


@pytest.mark.asyncio
async def test_diagnostics_sources(
    respx_mock: respx.MockRouter, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(config, "BOKKA_API_BASE_URL", "https://api.test")
    monkeypatch.setattr(config, "HTTP_RETRY_BACKOFF_SECONDS", 0.0)
    await init_http_client()
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
    respx_mock.get("https://api.test/api/v1/crews").mock(
        return_value=Response(
            200,
            json=[
                {
                    "id": "c1",
                    "driver": {"id": "d1", "name": "D", "role": "driver"},
                    "assistant": None,
                    "assistant2": None,
                    "vehicle": None,
                    "office": "HQ",
                    "division": None,
                }
            ],
        )
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/diagnostics/sources")
    await close_http_client()
    assert response.status_code == 200
    data = response.json()
    assert len(data["vehicles"]) == 1
    assert len(data["crews"]) == 1
