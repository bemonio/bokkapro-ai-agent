from api.crews import get_crews
from api.http_client import request
from api.vehicles import get_vehicles
from api.errors import ApiError
from planner.dtos import Coord, PlanResultDTO
from planner.solver import solve_plan
from planner.stops import get_today_stops
import config

_latest_plan: PlanResultDTO | None = None


async def build_today_plan() -> PlanResultDTO:
    vehicles = await get_vehicles()
    await get_crews()
    stops = await get_today_stops()
    depot = Coord(lat=config.DEPOT_LAT, lon=config.DEPOT_LON)
    plan = solve_plan(depot, stops, vehicles)
    global _latest_plan
    _latest_plan = plan
    return plan


async def publish_plan(plan: PlanResultDTO) -> None:
    response = await request("POST", config.REPORTING_POST_URL, json=plan.model_dump())
    if not 200 <= response.status_code < 300:
        raise ApiError(response.status_code, response.text[:100])


def get_latest_plan() -> PlanResultDTO | None:
    return _latest_plan
