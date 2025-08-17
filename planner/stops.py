from planner.dtos import Coord, TaskDTO, TimeWindow


async def get_today_stops() -> list[TaskDTO]:
    return [
        TaskDTO(
            id="t1",
            kind="pickup",
            location=Coord(lat=40.0, lon=-3.0),
            window=TimeWindow(start="09:00", end="12:00"),
            size=1,
        ),
        TaskDTO(
            id="t2",
            kind="delivery",
            location=Coord(lat=40.1, lon=-3.1),
            window=None,
            size=1,
        ),
        TaskDTO(
            id="t3",
            kind="pickup",
            location=Coord(lat=40.2, lon=-3.2),
            window=TimeWindow(start="10:00", end="16:00"),
            size=2,
        ),
        TaskDTO(
            id="t4",
            kind="delivery",
            location=Coord(lat=40.3, lon=-3.3),
            window=None,
            size=1,
        ),
    ]
