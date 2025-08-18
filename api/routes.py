"""FastAPI router for managing planned routes using async SQLAlchemy."""
from __future__ import annotations

import logging
from typing import AsyncGenerator, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload

from api.schemas import (
    RouteCreateSchema,
    RouteSchema,
    RouteSummarySchema,
    RouteTaskLinkSchema,
    ScheduleSubmitSchema,
)
from storage.routes import DB_PATH, Route as RouteEntity, RouteTaskLink as RouteTaskLinkEntity

logger = logging.getLogger(__name__)


DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"
engine = create_async_engine(DATABASE_URL, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:  # pragma: no cover - generator
        yield session


router = APIRouter(prefix="/routes", tags=["routes"])


def _build_route_entity(payload: RouteCreateSchema) -> RouteEntity:
    """Convert a route creation schema into a `RouteEntity`."""

    route = RouteEntity(
        date=payload.date,
        vehicle_id=payload.vehicle_id,
        crew_id=payload.crew_id,
        office_id=payload.office_id,
        total_distance=payload.total_distance,
        total_duration=payload.total_duration,
    )
    for task in payload.tasks:
        route.tasks.append(
            RouteTaskLinkEntity(
                task_id=task.task_id,
                order=task.order,
                estimated_start=task.estimated_start,
                estimated_end=task.estimated_end,
            )
        )
    return route


@router.get("/", response_model=List[RouteSummarySchema])
async def list_routes(session: AsyncSession = Depends(get_session)) -> List[RouteEntity]:
    """Return all routes with basic information."""

    result = await session.execute(select(RouteEntity))
    routes = result.scalars().all()
    logger.debug("Listing %d routes", len(routes))
    return routes


@router.get("/{route_id}", response_model=RouteSchema)
async def get_route(route_id: UUID, session: AsyncSession = Depends(get_session)) -> RouteEntity:
    """Return a route and its ordered tasks."""

    query = (
        select(RouteEntity)
        .where(RouteEntity.id == str(route_id))
        .options(selectinload(RouteEntity.tasks))
    )
    result = await session.execute(query)
    route = result.scalars().first()
    if route is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")
    # tasks relationship is configured with order_by so tasks come sorted
    return route


@router.post("/", response_model=RouteSchema, status_code=status.HTTP_201_CREATED)
async def create_route(
    payload: RouteCreateSchema, session: AsyncSession = Depends(get_session)
) -> RouteEntity:
    """Create a new route with its associated tasks."""

    route = _build_route_entity(payload)
    session.add(route)
    try:
        await session.commit()
    except Exception:  # pragma: no cover - safety net
        logger.exception("Failed to create route")
        await session.rollback()
        raise HTTPException(status_code=500, detail="Failed to create route")
    await session.refresh(route)
    return route


@router.delete("/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_route(route_id: UUID, session: AsyncSession = Depends(get_session)) -> Response:
    """Delete a route and its linked tasks."""

    route = await session.get(RouteEntity, str(route_id))
    if route is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")
    await session.delete(route)
    await session.commit()
    logger.info("Deleted route %s", route_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/schedule/submit")
async def submit_schedule(
    payload: ScheduleSubmitSchema, session: AsyncSession = Depends(get_session)
) -> dict[str, int]:
    """Submit a complete daily schedule of routes.

    Existing routes for the same vehicle and date are overwritten.
    """

    created = 0
    overwritten = 0

    for route_payload in payload.routes:
        query = select(RouteEntity).where(
            RouteEntity.date == route_payload.date,
            RouteEntity.vehicle_id == route_payload.vehicle_id,
        )
        result = await session.execute(query)
        existing = result.scalars().first()
        if existing is not None:
            await session.delete(existing)
            overwritten += 1
            logger.info(
                "Overwriting existing route for vehicle %s on %s",
                route_payload.vehicle_id,
                route_payload.date,
            )
        else:
            created += 1
            logger.info(
                "Creating route for vehicle %s on %s",
                route_payload.vehicle_id,
                route_payload.date,
            )

        new_route = _build_route_entity(route_payload)
        session.add(new_route)

    try:
        await session.commit()
    except Exception:  # pragma: no cover - safety net
        logger.exception("Failed to submit schedule")
        await session.rollback()
        raise HTTPException(status_code=500, detail="Failed to submit schedule")

    return {"created": created, "overwritten": overwritten}

