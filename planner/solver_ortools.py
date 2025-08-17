from __future__ import annotations

from datetime import datetime
import json
import logging
from typing import List, cast

from api.dtos import VehicleDTO
from planner.dtos import Coord, TaskDTO, VehiclePlanDTO, PlanResultDTO
from planner.metrics import distance_km, travel_minutes
import config

try:
    from ortools.constraint_solver import pywrapcp, routing_enums_pb2
except Exception:  # pragma: no cover
    raise

logger = logging.getLogger(__name__)


def _parse_time(value: str) -> int:
    h, m = value.split(":")
    return int(h) * 60 + int(m)


def _format_time(minutes: int) -> str:
    h = minutes // 60
    m = minutes % 60
    return f"{h:02d}:{m:02d}"


def solve_plan_ortools(
    depots: List[Coord], tasks: List[TaskDTO], vehicles: List[VehicleDTO]
) -> PlanResultDTO:
    horizon_start = _parse_time(config.PLANNING_HORIZON_START)
    horizon_end = _parse_time(config.PLANNING_HORIZON_END)

    locations: List[Coord] = list(depots) + [t.location for t in tasks]
    service_times: list[int] = [0] * len(depots) + [
        t.service_minutes or config.SERVICE_TIME_MINUTES_DEFAULT for t in tasks
    ]
    demands: list[int] = [0] * len(depots) + [t.size for t in tasks]

    windows: List[tuple[int, int]] = []
    for _ in depots:
        windows.append((horizon_start, horizon_end))
    for t in tasks:
        if t.window:
            ws = _parse_time(t.window.start)
            we = _parse_time(t.window.end)
        else:
            ws, we = horizon_start, horizon_end
        windows.append((ws, we))

    starts = [i % len(depots) for i in range(len(vehicles))]
    ends = [i % len(depots) for i in range(len(vehicles))]
    manager = pywrapcp.RoutingIndexManager(len(locations), len(vehicles), starts, ends)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index: int, to_index: int) -> int:
        from_node = cast(int, manager.IndexToNode(from_index))
        to_node = cast(int, manager.IndexToNode(to_index))
        a = locations[from_node]
        b = locations[to_node]
        return int(distance_km(a, b) * 1000)

    dist_cb = routing.RegisterTransitCallback(distance_callback)

    def time_callback(from_index: int, to_index: int) -> int:
        from_node = cast(int, manager.IndexToNode(from_index))
        to_node = cast(int, manager.IndexToNode(to_index))
        a = locations[from_node]
        b = locations[to_node]
        travel = travel_minutes(a, b, config.AVERAGE_SPEED_KMPH)
        service = service_times[from_node]
        return travel + service

    time_cb = routing.RegisterTransitCallback(time_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(time_cb)

    def demand_callback(index: int) -> int:
        node = cast(int, manager.IndexToNode(index))
        return demands[node]

    demand_cb_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_cb_index,
        0,
        [v.capacity for v in vehicles],
        True,
        "Capacity",
    )

    routing.AddDimension(time_cb, horizon_end, horizon_end, False, "Time")
    time_dim = routing.GetDimensionOrDie("Time")
    for node, (ws, we) in enumerate(windows):
        index = manager.NodeToIndex(node)
        time_dim.CumulVar(index).SetRange(ws, we)
    for vid in range(len(vehicles)):
        time_dim.CumulVar(routing.Start(vid)).SetRange(horizon_start, horizon_start)
        time_dim.CumulVar(routing.End(vid)).SetRange(horizon_start, horizon_end)

    routing.AddDimension(dist_cb, 0, 10**9, True, "Distance")
    dist_dim = routing.GetDimensionOrDie("Distance")

    # allow dropping tasks with penalty
    for node in range(len(depots), len(locations)):
        routing.AddDisjunction([manager.NodeToIndex(node)], 10_000)

    search_params = pywrapcp.DefaultRoutingSearchParameters()
    search_params.first_solution_strategy = getattr(
        routing_enums_pb2.FirstSolutionStrategy, config.SOLVER_FIRST_SOLUTION
    )
    search_params.local_search_metaheuristic = getattr(
        routing_enums_pb2.LocalSearchMetaheuristic, config.SOLVER_METAHEURISTIC
    )
    search_params.time_limit.seconds = config.SOLVER_TIMEOUT_SECONDS

    logger.info(json.dumps({"event": "solver_selected", "solver": "ortools"}))
    solution = routing.SolveWithParameters(search_params)
    if solution is None:
        logger.info(json.dumps({"event": "solver_timeout"}))
        generated = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        return PlanResultDTO(
            generated_at=generated,
            depot=depots[0],
            vehicle_plans=[],
            unscheduled=sorted(t.id for t in tasks),
            objective_minutes=0,
        )

    plans: List[VehiclePlanDTO] = []
    for vid, vehicle in enumerate(vehicles):
        index = routing.Start(vid)
        order: List[str] = []
        etas: List[str] = []
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            if node >= len(depots):
                task_idx = node - len(depots)
                order.append(tasks[task_idx].id)
                eta = solution.Value(time_dim.CumulVar(index))
                etas.append(_format_time(eta))
            index = solution.Value(routing.NextVar(index))
        end_index = routing.End(vid)
        route_time = solution.Value(time_dim.CumulVar(end_index)) - solution.Value(
            time_dim.CumulVar(routing.Start(vid))
        )
        route_km = solution.Value(dist_dim.CumulVar(end_index)) / 1000.0
        plans.append(
            VehiclePlanDTO(
                vehicle_id=vehicle.id,
                tasks_order=order,
                eta=etas,
                total_minutes=int(route_time),
                total_km=round(route_km, 2),
            )
        )

    unscheduled: List[str] = []
    for task_idx, task in enumerate(tasks):
        node = len(depots) + task_idx
        index = manager.NodeToIndex(node)
        if solution.Value(routing.NextVar(index)) == index:
            unscheduled.append(task.id)
    unscheduled.sort()
    if unscheduled:
        logger.info(
            json.dumps({"event": "tasks_unassigned", "count": len(unscheduled)})
        )

    objective = sum(p.total_minutes for p in plans)
    generated = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    return PlanResultDTO(
        generated_at=generated,
        depot=depots[0],
        vehicle_plans=plans,
        unscheduled=unscheduled,
        objective_minutes=objective,
    )
