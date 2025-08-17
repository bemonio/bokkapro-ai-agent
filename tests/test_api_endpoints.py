import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
import api.api as api_module
import planner.service as service
from api.dtos import VehicleDTO
import config
import pytest


def test_api_endpoints(monkeypatch: pytest.MonkeyPatch) -> None:
    config.DEPOT_LAT = 0.0
    config.DEPOT_LON = 0.0
    config.PLANNING_HORIZON_START = "08:00"

    async def fake_get_vehicles() -> list[VehicleDTO]:
        return [VehicleDTO(id="v1", plate="p", capacity=10, office="o", division=None)]

    async def fake_get_crews() -> list[object]:
        return []

    async def fake_publish(plan: object) -> None:
        return None

    monkeypatch.setattr(service, "get_vehicles", fake_get_vehicles)
    monkeypatch.setattr(service, "get_crews", fake_get_crews)
    monkeypatch.setattr(api_module, "publish_plan", fake_publish)

    client = TestClient(api_module.app)
    response = client.post("/agent/run")
    assert response.status_code == 200
    data = response.json()
    assert {"vehicles", "tasks", "unscheduled"} <= data.keys()
    preview = client.get("/agent/plan/preview")
    assert preview.status_code == 200
    plan = preview.json()
    assert "vehicle_plans" in plan
