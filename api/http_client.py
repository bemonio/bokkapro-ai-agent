import asyncio
from typing import Any
import httpx

from api.errors import NetworkError
from config import HTTP_RETRY_ATTEMPTS, HTTP_RETRY_BACKOFF_SECONDS, HTTP_TIMEOUT_SECONDS
import config

_client: httpx.AsyncClient | None = None


async def init_http_client() -> None:
    global _client
    if _client is None:

        async def add_auth_header(request: httpx.Request) -> None:
            if config.AUTH_TOKEN:
                request.headers["Authorization"] = f"Bearer {config.AUTH_TOKEN}"

        _client = httpx.AsyncClient(
            timeout=HTTP_TIMEOUT_SECONDS,
            event_hooks={"request": [add_auth_header]},
        )


async def close_http_client() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


async def request(method: str, url: str, **kwargs: Any) -> httpx.Response:
    if _client is None:
        raise RuntimeError("HTTP client not initialized")
    backoff = HTTP_RETRY_BACKOFF_SECONDS
    for attempt in range(HTTP_RETRY_ATTEMPTS):
        try:
            response = await _client.request(method, url, **kwargs)
        except (
            httpx.ConnectError,
            httpx.ConnectTimeout,
            httpx.ReadTimeout,
        ) as exc:
            if attempt == HTTP_RETRY_ATTEMPTS - 1:
                raise NetworkError() from exc
        else:
            if response.status_code in {429} or 500 <= response.status_code < 600:
                if attempt == HTTP_RETRY_ATTEMPTS - 1:
                    return response
            else:
                return response
        await asyncio.sleep(backoff * 2**attempt)
    return response
