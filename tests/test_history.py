import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from planner.dtos import PlanResultDTO, Coord
import storage.history as history
import config
import pytest


def _plan(idx: int) -> PlanResultDTO:
    return PlanResultDTO(
        generated_at=f"2024-01-01T00:00:0{idx}Z",
        depot=Coord(lat=0.0, lon=0.0),
        vehicle_plans=[],
        unscheduled=[],
    )


def test_history_save_and_fetch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(history, "DB_PATH", tmp_path / "history.db")
    monkeypatch.setattr(config, "PLAN_HISTORY_SIZE", 2)
    history.init_db()
    history.save_plan(_plan(1))
    history.save_plan(_plan(2))
    history.save_plan(_plan(3))
    plans = history.get_recent_plans(5)
    assert len(plans) == 2
    assert plans[0].generated_at == "2024-01-01T00:00:03Z"
    assert plans[1].generated_at == "2024-01-01T00:00:02Z"
