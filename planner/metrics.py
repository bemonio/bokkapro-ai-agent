import math
from planner.dtos import Coord
import config


def distance_km(a: Coord, b: Coord) -> float:
    r = 6371.0
    phi1 = math.radians(a.lat)
    phi2 = math.radians(b.lat)
    dphi = math.radians(b.lat - a.lat)
    dlambda = math.radians(b.lon - a.lon)
    d = (
        2
        * r
        * math.asin(
            math.sqrt(
                math.sin(dphi / 2) ** 2
                + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
            )
        )
    )
    return d


def travel_minutes(a: Coord, b: Coord, speed_kmph: int) -> int:
    km = distance_km(a, b)
    minutes = km / speed_kmph * 60
    return int(minutes + 0.5)


def haversine_minutes(a: Coord, b: Coord) -> int:
    return travel_minutes(a, b, config.AVERAGE_SPEED_KMPH)
