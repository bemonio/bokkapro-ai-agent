"""Route planning logic using OR-Tools and temporary fallback utilities."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import datetime
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


async def generate_basic_schedule(base_url: str = "http://localhost:8000/") -> dict[str, Any] | None:
    """Generate and submit a very simple schedule.

    This placeholder will be replaced by a proper optimization module later.

    The function fetches active vehicles, crews and tasks, assigns tasks in the
    input order to available vehicles/crews grouped by office, then submits the
    generated schedule to the local FastAPI endpoint.
    """

    async with httpx.AsyncClient(base_url=base_url) as client:
        try:
            vehicles_req = client.get("/vehicles/active")
            crews_req = client.get("/crews/active")
            tasks_req = client.get("/tasks/active")
            vehicles_res, crews_res, tasks_res = await asyncio.gather(
                vehicles_req, crews_req, tasks_req
            )
            vehicles_res.raise_for_status()
            crews_res.raise_for_status()
            tasks_res.raise_for_status()
            vehicles = vehicles_res.json()
            crews = crews_res.json()
            tasks = tasks_res.json()
        except Exception:  # pragma: no cover - network failure safety
            logger.exception("Failed to fetch data for schedule generation")
            return None

    tasks_by_office: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for task in tasks:
        office_id = task.get("office_id") or task.get("office")
        if office_id:
            tasks_by_office[office_id].append(task)

    vehicles_by_office: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for vehicle in vehicles:
        office_id = vehicle.get("office_id") or vehicle.get("office")
        vehicles_by_office[office_id].append(vehicle)

    crews_by_office: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for crew in crews:
        office_id = crew.get("office_id") or crew.get("office")
        crews_by_office[office_id].append(crew)

    schedule_date = datetime.utcnow().date().isoformat()
    routes: list[dict[str, Any]] = []

    for office_id, office_tasks in tasks_by_office.items():
        office_vehicles = vehicles_by_office.get(office_id, [])
        office_crews = crews_by_office.get(office_id, [])
        if not office_vehicles:
            logger.warning("No vehicles available for office %s", office_id)
            continue

        route_map: dict[str, dict[str, Any]] = {}
        for idx, vehicle in enumerate(office_vehicles):
            crew_id = office_crews[idx]["id"] if idx < len(office_crews) else None
            route_map[vehicle["id"]] = {
                "vehicle_id": vehicle["id"],
                "crew_id": crew_id,
                "office_id": office_id,
                "tasks": [],
            }

        for idx, task in enumerate(office_tasks):
            vehicle = office_vehicles[idx % len(office_vehicles)]
            vehicle_route = route_map[vehicle["id"]]
            order = len(vehicle_route["tasks"]) + 1
            now_iso = datetime.utcnow().isoformat()
            vehicle_route["tasks"].append(
                {
                    "task_id": task.get("id"),
                    "order": order,
                    "estimated_start": now_iso,
                    "estimated_end": now_iso,
                }
            )

        routes.extend(
            route
            for route in route_map.values()
            if route["tasks"]
        )

    payload = {"date": schedule_date, "routes": routes}

    async with httpx.AsyncClient(base_url=base_url) as client:
        try:
            response = await client.post("/routes/schedule/submit", json=payload)
            if 200 <= response.status_code < 300:
                logger.info("Schedule submission successful: %s", response.json())
            else:
                logger.error(
                    "Schedule submission failed: %s %s",
                    response.status_code,
                    response.text,
                )
        except Exception:  # pragma: no cover - network failure safety
            logger.exception("Error submitting schedule")

    return payload


class Planner:
    """Placeholder planner using OR-Tools."""

    def plan(self) -> None:
        """Perform planning and return schedule."""
        # TODO: Implement planning algorithm
        return None
