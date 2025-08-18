"""Pydantic schemas for route planning API."""
from __future__ import annotations

from datetime import date, datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, ValidationInfo, field_validator


class RouteTaskLinkBase(BaseModel):
    """Base information for a task linked to a route."""

    task_id: str
    order: int
    estimated_start: datetime | None = None
    estimated_end: datetime | None = None


class RouteTaskLinkSchema(RouteTaskLinkBase):
    """Full representation of a route-task link."""

    id: UUID
    route_id: UUID

    class Config:
        from_attributes = True


class RouteTaskLinkCreate(RouteTaskLinkBase):
    """Schema used when creating a link between a route and a task."""


class RouteBase(BaseModel):
    """Shared route attributes."""

    date: date
    vehicle_id: str
    crew_id: str | None = None
    office_id: str
    total_distance: float = 0
    total_duration: float = 0


class RouteCreateSchema(RouteBase):
    """Schema for route creation including ordered tasks."""

    tasks: List[RouteTaskLinkCreate] = []


class RouteSchema(RouteBase):
    """Full route representation including tasks."""

    id: UUID
    created_at: datetime
    tasks: List[RouteTaskLinkSchema] = []

    class Config:
        from_attributes = True


class RouteSummarySchema(BaseModel):
    """Basic information about a route used in listings."""

    id: UUID
    date: date
    vehicle_id: str
    crew_id: str | None = None
    office_id: str

    class Config:
        from_attributes = True


class ScheduleSubmitSchema(BaseModel):
    """Schema for submitting a full day of routes."""

    date: date
    routes: List[RouteCreateSchema]

    # Inject the shared date into each route before validation
    @field_validator("routes", mode="before")
    @classmethod
    def _apply_date(cls, v: List[dict], info: ValidationInfo) -> List[dict]:
        sched_date = info.data.get("date")
        if sched_date is not None:
            for r in v:
                r.setdefault("date", sched_date)
        return v

