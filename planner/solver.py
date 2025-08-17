from datetime import datetime
from planner.dtos import Coord, PlanResultDTO, TaskDTO, VehiclePlanDTO
from api.dtos import VehicleDTO
from planner.metrics import haversine_minutes
import config


def _parse_time(value: str) -> int:
    h, m = value.split(":")
    return int(h) * 60 + int(m)


def _format_time(minutes: int) -> str:
    h = minutes // 60
    m = minutes % 60
    return f"{h:02d}:{m:02d}"


def solve_plan(
    depot: Coord, tasks: list[TaskDTO], vehicles: list[VehicleDTO]
) -> PlanResultDTO:
    start = _parse_time(config.PLANNING_HORIZON_START)
    remaining = list(tasks)
    plans: list[VehiclePlanDTO] = []
    for vehicle in vehicles:
        cap = vehicle.capacity
        loc = depot
        time = start
        order: list[str] = []
        etas: list[str] = []
        idx = 0
        while idx < len(remaining):
            task = remaining[idx]
            if task.size > cap:
                idx += 1
                continue
            travel = haversine_minutes(loc, task.location)
            arrival = time + travel
            if task.window:
                ws = _parse_time(task.window.start)
                we = _parse_time(task.window.end)
                if arrival < ws:
                    arrival = ws
                if arrival > we:
                    idx += 1
                    continue
            time = arrival
            cap -= task.size
            order.append(task.id)
            etas.append(_format_time(time))
            loc = task.location
            remaining.pop(idx)
        plans.append(VehiclePlanDTO(vehicle_id=vehicle.id, tasks_order=order, eta=etas))
    unscheduled = [t.id for t in remaining]
    generated = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    return PlanResultDTO(
        generated_at=generated,
        depot=depot,
        vehicle_plans=plans,
        unscheduled=unscheduled,
    )
