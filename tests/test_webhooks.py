import json
import hashlib
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient

import api.api as api_module
import config


def _signature(body: dict[str, object]) -> str:
    raw = json.dumps(body, separators=(",", ":"))
    return hashlib.sha256((config.WEBHOOK_SECRET + raw).encode()).hexdigest()


def test_webhook_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    config.WEBHOOK_SECRET = "s"
    called = False

    async def fake_replan() -> None:
        nonlocal called
        called = True

    monkeypatch.setattr(api_module, "replan_incremental", fake_replan)
    client = TestClient(api_module.app)
    body: dict[str, object] = {"id": "1", "location": {}, "window": None, "size": 1}
    sig = _signature(body)
    resp = client.post(
        "/webhooks/pickup_created", json=body, headers={"X-Signature": sig}
    )
    assert resp.status_code == 200
    assert called


def test_webhook_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    config.WEBHOOK_SECRET = "s"
    called = False

    async def fake_replan() -> None:
        nonlocal called
        called = True

    monkeypatch.setattr(api_module, "replan_incremental", fake_replan)
    client = TestClient(api_module.app)
    body: dict[str, str] = {"id": "1"}
    resp = client.post(
        "/webhooks/vehicle_status_changed", json=body, headers={"X-Signature": "bad"}
    )
    assert resp.status_code == 401
    assert not called
