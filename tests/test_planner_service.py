import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pytest
from api.dtos import VehicleDTO
import planner.service as service
from planner.dtos import TaskDTO, Coord
import config


@pytest.mark.asyncio
async def test_build_today_plan(monkeypatch: pytest.MonkeyPatch) -> None:
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

    plan = await service.build_today_plan()
    assert service.get_latest_plan() is plan
    stops_data = await fake_get_today_stops()
    total_assigned = sum(len(v.tasks_order) for v in plan.vehicle_plans)
    assert total_assigned + len(plan.unscheduled) == len(stops_data)
