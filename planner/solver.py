from datetime import datetime
from planner.dtos import Coord, PlanResultDTO, TaskDTO, VehiclePlanDTO
from api.dtos import VehicleDTO
from planner.metrics import distance_km, travel_minutes
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
        total_dist = 0.0
        idx = 0
        while idx < len(remaining):
            task = remaining[idx]
            if task.size > cap:
                idx += 1
                continue
            travel = travel_minutes(loc, task.location, config.AVERAGE_SPEED_KMPH)
            arrival = time + travel
            if task.window:
                ws = _parse_time(task.window.start)
                we = _parse_time(task.window.end)
                if arrival < ws:
                    arrival = ws
                if arrival > we:
                    idx += 1
                    continue
            service = task.service_minutes or config.SERVICE_TIME_MINUTES_DEFAULT
            distance = distance_km(loc, task.location)
            total_dist += distance
            cap -= task.size
            order.append(task.id)
            etas.append(_format_time(arrival))
            time = arrival + service
            loc = task.location
            remaining.pop(idx)
        total_minutes = time - start
        plans.append(
            VehiclePlanDTO(
                vehicle_id=vehicle.id,
                tasks_order=order,
                eta=etas,
                total_minutes=total_minutes,
                total_km=round(total_dist, 2),
            )
        )
    unscheduled = sorted(t.id for t in remaining)
    generated = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    objective = sum(p.total_minutes for p in plans)
    return PlanResultDTO(
        generated_at=generated,
        depot=depot,
        vehicle_plans=plans,
        unscheduled=unscheduled,
        objective_minutes=objective,
    )
