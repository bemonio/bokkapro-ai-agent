import asyncio
from typing import Any
from api.api import app
from api.http_client import close_http_client, init_http_client
from api.vehicles import get_vehicles
from api.crews import get_crews
from storage.history import init_db
import scheduler

__all__ = ["app"]


@app.on_event("startup")
async def startup() -> None:
    await init_http_client()
    init_db()
    scheduler.start()


@app.on_event("shutdown")
async def shutdown() -> None:
    await close_http_client()
    await scheduler.shutdown()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/diagnostics/sources")
async def diagnostics_sources() -> dict[str, Any]:
    vehicles_task = asyncio.create_task(get_vehicles())
    crews_task = asyncio.create_task(get_crews())
    vehicles, crews = await asyncio.gather(vehicles_task, crews_task)
    return {"vehicles": vehicles, "crews": crews}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
