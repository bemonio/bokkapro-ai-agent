from typing import Literal
from pydantic import BaseModel, ConfigDict


class Coord(BaseModel):
    lat: float
    lon: float
    model_config = ConfigDict(extra="ignore")


class TimeWindow(BaseModel):
    start: str
    end: str
    model_config = ConfigDict(extra="ignore")


class TaskDTO(BaseModel):
    id: str
    kind: Literal["pickup", "delivery"]
    location: Coord
    window: TimeWindow | None
    size: int
    service_minutes: int | None = None
    model_config = ConfigDict(extra="ignore")


class VehiclePlanDTO(BaseModel):
    vehicle_id: str
    tasks_order: list[str]
    eta: list[str]
    total_minutes: int
    total_km: float
    model_config = ConfigDict(extra="ignore")


class PlanResultDTO(BaseModel):
    generated_at: str
    depot: Coord
    vehicle_plans: list[VehiclePlanDTO]
    unscheduled: list[str]
    objective_minutes: int
    model_config = ConfigDict(extra="ignore")
