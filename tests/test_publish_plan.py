import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pytest
from planner.dtos import Coord, PlanResultDTO
from planner.service import publish_plan
from api.errors import ApiError


class DummyResponse:
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code
        self.text = ""


@pytest.mark.asyncio
async def test_publish_plan_success(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_request(method: str, url: str, **kwargs: object) -> DummyResponse:
        return DummyResponse(200)

    monkeypatch.setattr("planner.service.request", fake_request)
    plan = PlanResultDTO(
        generated_at="2024-01-01T00:00:00Z",
        depot=Coord(lat=0.0, lon=0.0),
        vehicle_plans=[],
        unscheduled=[],
        objective_minutes=0,
    )
    await publish_plan(plan)


@pytest.mark.asyncio
async def test_publish_plan_error(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_request(method: str, url: str, **kwargs: object) -> DummyResponse:
        return DummyResponse(500)

    monkeypatch.setattr("planner.service.request", fake_request)
    plan = PlanResultDTO(
        generated_at="2024-01-01T00:00:00Z",
        depot=Coord(lat=0.0, lon=0.0),
        vehicle_plans=[],
        unscheduled=[],
        objective_minutes=0,
    )
    with pytest.raises(ApiError):
        await publish_plan(plan)
