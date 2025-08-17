import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from planner.dtos import Coord, TaskDTO, TimeWindow
from planner.solver_ortools import solve_plan_ortools
from api.dtos import VehicleDTO
import config


def test_solver_ortools_basic() -> None:
    config.PLANNING_HORIZON_START = "08:00"
    depots = [Coord(lat=0.0, lon=0.0)]
    tasks = [
        TaskDTO(
            id="a",
            kind="pickup",
            location=Coord(lat=0.0, lon=0.01),
            window=None,
            size=2,
        ),
        TaskDTO(
            id="b",
            kind="delivery",
            location=Coord(lat=0.0, lon=0.02),
            window=TimeWindow(start="09:00", end="10:00"),
            size=2,
        ),
        TaskDTO(
            id="c",
            kind="pickup",
            location=Coord(lat=1.0, lon=0.0),
            window=TimeWindow(start="09:00", end="09:30"),
            size=2,
        ),
    ]
    vehicles = [
        VehicleDTO(id="v1", plate="p1", capacity=4, office="o", division=None),
        VehicleDTO(id="v2", plate="p2", capacity=2, office="o", division=None),
    ]
    plan = solve_plan_ortools(depots, tasks, vehicles)
    assigned = [t for v in plan.vehicle_plans for t in v.tasks_order]
    assert set(assigned) == {"a", "b"}
    assert plan.unscheduled == ["c"]
    for vp in plan.vehicle_plans:
        assert vp.total_minutes >= 0
        assert vp.total_km >= 0.0
