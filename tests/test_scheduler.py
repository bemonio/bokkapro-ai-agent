import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pytest

import scheduler
from planner.dtos import PlanResultDTO, Coord


@pytest.mark.asyncio
async def test_scheduler_job(monkeypatch: pytest.MonkeyPatch) -> None:
    called = False

    async def fake_build() -> PlanResultDTO:
        nonlocal called
        called = True
        return PlanResultDTO(
            generated_at="2024-01-01T00:00:00Z",
            depot=Coord(lat=0.0, lon=0.0),
            vehicle_plans=[],
            unscheduled=[],
            objective_minutes=0,
        )

    async def fake_publish(plan: PlanResultDTO) -> None:
        return None

    monkeypatch.setattr(scheduler, "build_today_plan", fake_build)
    monkeypatch.setattr(scheduler, "publish_plan", fake_publish)

    await scheduler._run_job()
    assert called
