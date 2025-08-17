"""Dataclasses for vehicles, tasks, and related entities."""

from dataclasses import dataclass


@dataclass
class Vehicle:
    """Represents a delivery vehicle."""
    id: int
    status: str


@dataclass
class Task:
    """Represents a delivery or pickup task."""
    id: int
    type: str
