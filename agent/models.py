"""Dataclasses representing core domain entities."""

from dataclasses import dataclass


@dataclass
class Vehicle:
    """Placeholder dataclass for vehicles."""
    id: int
    name: str


@dataclass
class Task:
    """Placeholder dataclass for pickup or delivery tasks."""
    id: int
    location: str
    type: str  # "pickup" or "delivery"
