"""FastAPI router for managing planned routes."""
from __future__ import annotations

import logging
from datetime import date, datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from storage.routes import Route, RouteTaskLink, SessionLocal

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/routes", tags=["routes"])


# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------
class RouteTaskLinkBase(BaseModel):
    """Base information for a task assigned to a route."""

    task_id: str
    order: int
    estimated_start: datetime | None = None
    estimated_end: datetime | None = None


class RouteTaskLinkSchema(RouteTaskLinkBase):
    """Schema representing a task link within a route."""

    id: UUID
    route_id: UUID

    class Config:
        from_attributes = True


class RouteTaskLinkCreate(RouteTaskLinkBase):
    """Schema used when creating task links."""


class RouteBase(BaseModel):
    """Shared route attributes."""

    date: date
    vehicle_id: str
    crew_id: str | None = None
    office_id: str
    total_distance: float = 0
    total_duration: float = 0


class RouteCreateSchema(RouteBase):
    """Schema for creating routes."""

    tasks: List[RouteTaskLinkCreate] = []


class RouteSchema(RouteBase):
    """Full route representation."""

    id: UUID
    created_at: datetime
    tasks: List[RouteTaskLinkSchema] = []

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Database session dependency
# ---------------------------------------------------------------------------

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# CRUD Endpoints
# ---------------------------------------------------------------------------

@router.get("/", response_model=List[RouteSchema])
def list_routes(db: Session = Depends(get_db)) -> List[Route]:
    """Return all stored routes."""

    routes = db.query(Route).all()
    logger.debug("Listing %d routes", len(routes))
    return routes


@router.get("/{route_id}", response_model=RouteSchema)
def get_route(route_id: UUID, db: Session = Depends(get_db)) -> Route:
    """Retrieve a single route by its identifier."""

    route = db.get(Route, str(route_id))
    if route is None:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


@router.post("/", response_model=RouteSchema, status_code=201)
def create_route(payload: RouteCreateSchema, db: Session = Depends(get_db)) -> Route:
    """Create a new route with its associated tasks."""

    route = Route(
        date=payload.date,
        vehicle_id=payload.vehicle_id,
        crew_id=payload.crew_id,
        office_id=payload.office_id,
        total_distance=payload.total_distance,
        total_duration=payload.total_duration,
    )
    for task in payload.tasks:
        route.tasks.append(
            RouteTaskLink(
                task_id=task.task_id,
                order=task.order,
                estimated_start=task.estimated_start,
                estimated_end=task.estimated_end,
            )
        )
    db.add(route)
    db.commit()
    db.refresh(route)
    logger.info("Created route %s", route.id)
    return route


@router.delete("/{route_id}", status_code=204)
def delete_route(route_id: UUID, db: Session = Depends(get_db)) -> Response:
    """Delete a route and its task links."""

    route = db.get(Route, str(route_id))
    if route is None:
        raise HTTPException(status_code=404, detail="Route not found")
    db.delete(route)
    db.commit()
    logger.info("Deleted route %s", route_id)
    return Response(status_code=204)
