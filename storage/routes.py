from __future__ import annotations

"""Database models for storing route planning results."""

from datetime import date, datetime
from pathlib import Path
from uuid import uuid4

from sqlalchemy import (
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)


class Base(DeclarativeBase):
    """Base class for all ORM models."""


# Database setup
DB_PATH = Path(__file__).with_name("routes.db")
engine = create_engine(f"sqlite:///{DB_PATH}", future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Route(Base):
    """Represents a planned route for a vehicle on a given day."""

    __tablename__ = "routes"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    vehicle_id: Mapped[str] = mapped_column(String, ForeignKey("vehicles.id"))
    crew_id: Mapped[str | None] = mapped_column(String, ForeignKey("crews.id"))
    office_id: Mapped[str] = mapped_column(String, ForeignKey("offices.id"))
    total_distance: Mapped[float] = mapped_column(Float, default=0)
    total_duration: Mapped[float] = mapped_column(Float, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    tasks: Mapped[list["RouteTaskLink"]] = relationship(
        back_populates="route",
        cascade="all, delete-orphan",
        order_by="RouteTaskLink.order",
    )


class RouteTaskLink(Base):
    """Associates tasks to routes and preserves task order."""

    __tablename__ = "route_task_links"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    route_id: Mapped[str] = mapped_column(String, ForeignKey("routes.id"))
    task_id: Mapped[str] = mapped_column(String, ForeignKey("tasks.id"))
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_start: Mapped[datetime | None] = mapped_column(DateTime)
    estimated_end: Mapped[datetime | None] = mapped_column(DateTime)

    route: Mapped[Route] = relationship(back_populates="tasks")


def init_db() -> None:
    """Initializes the routes database and creates tables."""

    Base.metadata.create_all(bind=engine)
