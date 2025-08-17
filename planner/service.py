from api.crews import get_crews
from api.http_client import request
from api.vehicles import get_vehicles
from api.errors import ApiError
from planner.dtos import Coord, PlanResultDTO
from planner.solver import solve_plan
from planner.stops_api import get_today_stops
from storage.history import save_plan
import config
import json
import time
import logging

try:
    from planner.solver_ortools import solve_plan_ortools

    _HAS_ORTOOLS = True
except Exception:  # pragma: no cover
    _HAS_ORTOOLS = False

try:  # optional prometheus
    from prometheus_client import Counter, Histogram

    _METRIC_RUNS = Counter("planner_runs_total", "Number of planner runs")
    _METRIC_RUNTIME = Histogram("planner_runtime_ms", "Planner runtime ms")
except Exception:  # pragma: no cover
    _METRIC_RUNS = None
    _METRIC_RUNTIME = None

logger = logging.getLogger(__name__)

if _HAS_ORTOOLS:
    logger.info(json.dumps({"event": "solver_selected", "solver": "ortools"}))
else:
    logger.info(json.dumps({"event": "solver_selected", "solver": "heuristic"}))

_latest_plan: PlanResultDTO | None = None
_latest_metrics: dict[str, float | int] | None = None


async def build_today_plan() -> PlanResultDTO:
    vehicles = await get_vehicles()
    await get_crews()
    stops = await get_today_stops()
    logger.info(
        json.dumps(
            {"event": "planner_start", "tasks": len(stops), "vehicles": len(vehicles)}
        )
    )
    start_time = time.time()
    if _HAS_ORTOOLS:
        if config.USE_MULTI_DEPOT:
            depots = [Coord(lat=config.DEPOT_LAT, lon=config.DEPOT_LON)]
        else:
            depots = [Coord(lat=config.DEPOT_LAT, lon=config.DEPOT_LON)]
        plan = solve_plan_ortools(depots, stops, vehicles)
    else:
        depot = Coord(lat=config.DEPOT_LAT, lon=config.DEPOT_LON)
        plan = solve_plan(depot, stops, vehicles)
    runtime_ms = int((time.time() - start_time) * 1000)
    if _METRIC_RUNS:
        _METRIC_RUNS.inc()
    if _METRIC_RUNTIME:
        _METRIC_RUNTIME.observe(runtime_ms)
    global _latest_plan, _latest_metrics
    _latest_plan = plan
    tasks_scheduled = sum(len(v.tasks_order) for v in plan.vehicle_plans)
    total_minutes = sum(v.total_minutes for v in plan.vehicle_plans)
    total_km = sum(v.total_km for v in plan.vehicle_plans)
    _latest_metrics = {
        "tasks_total": len(stops),
        "tasks_scheduled": tasks_scheduled,
        "tasks_unscheduled": len(plan.unscheduled),
        "total_minutes": total_minutes,
        "total_km": total_km,
        "runtime_ms": runtime_ms,
    }
    if plan.unscheduled:
        logger.info(
            json.dumps({"event": "tasks_unassigned", "count": len(plan.unscheduled)})
        )
    logger.info(
        json.dumps(
            {
                "event": "planner_end",
                "runtime_ms": runtime_ms,
                "objective_minutes": plan.objective_minutes,
            }
        )
    )
    save_plan(plan)
    return plan


async def publish_plan(plan: PlanResultDTO) -> None:
    response = await request("POST", config.REPORTING_POST_URL, json=plan.model_dump())
    if not 200 <= response.status_code < 300:
        raise ApiError(response.status_code, response.text[:100])


async def replan_incremental() -> PlanResultDTO:
    vehicles = await get_vehicles()
    stops = await get_today_stops()
    logger.info(
        json.dumps(
            {"event": "planner_start", "tasks": len(stops), "vehicles": len(vehicles)}
        )
    )
    start_time = time.time()
    if _HAS_ORTOOLS:
        if config.USE_MULTI_DEPOT:
            depots = [Coord(lat=config.DEPOT_LAT, lon=config.DEPOT_LON)]
        else:
            depots = [Coord(lat=config.DEPOT_LAT, lon=config.DEPOT_LON)]
        plan = solve_plan_ortools(depots, stops, vehicles)
    else:
        depot = Coord(lat=config.DEPOT_LAT, lon=config.DEPOT_LON)
        plan = solve_plan(depot, stops, vehicles)
    runtime_ms = int((time.time() - start_time) * 1000)
    if _METRIC_RUNS:
        _METRIC_RUNS.inc()
    if _METRIC_RUNTIME:
        _METRIC_RUNTIME.observe(runtime_ms)
    global _latest_plan, _latest_metrics
    _latest_plan = plan
    tasks_scheduled = sum(len(v.tasks_order) for v in plan.vehicle_plans)
    total_minutes = sum(v.total_minutes for v in plan.vehicle_plans)
    total_km = sum(v.total_km for v in plan.vehicle_plans)
    _latest_metrics = {
        "tasks_total": len(stops),
        "tasks_scheduled": tasks_scheduled,
        "tasks_unscheduled": len(plan.unscheduled),
        "total_minutes": total_minutes,
        "total_km": total_km,
        "runtime_ms": runtime_ms,
    }
    if plan.unscheduled:
        logger.info(
            json.dumps({"event": "tasks_unassigned", "count": len(plan.unscheduled)})
        )
    logger.info(
        json.dumps(
            {
                "event": "planner_end",
                "runtime_ms": runtime_ms,
                "objective_minutes": plan.objective_minutes,
            }
        )
    )
    save_plan(plan)
    return plan


def get_latest_plan() -> PlanResultDTO | None:
    return _latest_plan


def get_plan_metrics() -> dict[str, float | int] | None:
    return _latest_metrics
