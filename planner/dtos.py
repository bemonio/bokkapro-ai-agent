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
    model_config = ConfigDict(extra="ignore")


class VehiclePlanDTO(BaseModel):
    vehicle_id: str
    tasks_order: list[str]
    eta: list[str]
    model_config = ConfigDict(extra="ignore")


class PlanResultDTO(BaseModel):
    generated_at: str
    depot: Coord
    vehicle_plans: list[VehiclePlanDTO]
    unscheduled: list[str]
    model_config = ConfigDict(extra="ignore")
