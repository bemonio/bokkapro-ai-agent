import math
from planner.dtos import Coord


def haversine_minutes(a: Coord, b: Coord) -> int:
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
    minutes = d / 40 * 60
    return int(minutes + 0.5)
