import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pytest
import respx
from httpx import Response, Request

import config
from api.http_client import init_http_client, close_http_client, request


@pytest.mark.asyncio
async def test_auth_header_sent(
    respx_mock: respx.MockRouter, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(config, "AUTH_TOKEN", "token123")
    await init_http_client()

    def handler(req: Request) -> Response:
        assert req.headers.get("Authorization") == "Bearer token123"
        return Response(200)

    respx_mock.get("https://example.com").mock(side_effect=handler)
    await request("GET", "https://example.com")
    await close_http_client()
