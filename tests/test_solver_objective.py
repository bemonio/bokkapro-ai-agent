import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from planner.dtos import Coord, TaskDTO
from planner.solver_ortools import solve_plan_ortools
from api.dtos import VehicleDTO
import config


def _make_tasks() -> list[TaskDTO]:
    return [
        TaskDTO(
            id="a",
            kind="pickup",
            location=Coord(lat=0.0, lon=0.01),
            window=None,
            size=1,
        ),
        TaskDTO(
            id="b",
            kind="pickup",
            location=Coord(lat=0.0, lon=0.02),
            window=None,
            size=1,
        ),
    ]


def test_speed_affects_objective() -> None:
    depots = [Coord(lat=0.0, lon=0.0)]
    vehicles = [VehicleDTO(id="v1", plate="p", capacity=5, office="o", division=None)]
    config.AVERAGE_SPEED_KMPH = 40
    plan_fast = solve_plan_ortools(depots, _make_tasks(), vehicles)
    config.AVERAGE_SPEED_KMPH = 20
    plan_slow = solve_plan_ortools(depots, _make_tasks(), vehicles)
    assert plan_slow.objective_minutes > plan_fast.objective_minutes


def test_service_time_affects_objective() -> None:
    depots = [Coord(lat=0.0, lon=0.0)]
    vehicles = [VehicleDTO(id="v1", plate="p", capacity=5, office="o", division=None)]
    config.AVERAGE_SPEED_KMPH = 40
    tasks = _make_tasks()
    tasks[0].service_minutes = 5
    plan1 = solve_plan_ortools(depots, tasks, vehicles)
    tasks = _make_tasks()
    tasks[0].service_minutes = 20
    plan2 = solve_plan_ortools(depots, tasks, vehicles)
    assert plan2.objective_minutes > plan1.objective_minutes
