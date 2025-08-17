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


def _setup(monkeypatch: pytest.MonkeyPatch) -> None:
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

    monkeypatch.setattr(service, "get_vehicles", fake_get_vehicles)
    monkeypatch.setattr(service, "get_crews", fake_get_crews)
    monkeypatch.setattr(service, "get_today_stops", fake_get_today_stops)
    monkeypatch.setattr(service, "save_plan", lambda plan: None)

    async def fake_publish(plan: object) -> None:
        return None

    monkeypatch.setattr(api_module, "publish_plan", fake_publish)


def test_api_metrics(monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(monkeypatch)
    client = TestClient(api_module.app)
    assert client.post("/agent/run").status_code == 200
    resp = client.get("/agent/plan/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert data["tasks_total"] == 1
    assert data["tasks_scheduled"] == 1
    assert data["tasks_unscheduled"] == 0
    assert data["tasks_total"] == data["tasks_scheduled"] + data["tasks_unscheduled"]
    assert data["total_minutes"] >= 0
    assert data["total_km"] >= 0
    assert data["runtime_ms"] >= 0
