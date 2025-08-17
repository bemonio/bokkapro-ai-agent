import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
import api.api as api_module
import planner.service as service
from api.dtos import VehicleDTO
from planner.dtos import TaskDTO, Coord
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

    async def fake_get_today_stops() -> list[TaskDTO]:
        return [
            TaskDTO(
                id="t1",
                kind="pickup",
                location=Coord(lat=0.0, lon=0.0),
                window=None,
                size=1,
            )
        ]

    async def fake_publish(plan: object) -> None:
        return None

    monkeypatch.setattr(service, "get_vehicles", fake_get_vehicles)
    monkeypatch.setattr(service, "get_crews", fake_get_crews)
    monkeypatch.setattr(service, "get_today_stops", fake_get_today_stops)
    monkeypatch.setattr(service, "save_plan", lambda plan: None)
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
