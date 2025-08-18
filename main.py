import asyncio
import logging
from typing import Any
from api.api import app
from api.http_client import close_http_client, init_http_client
from api.vehicles import get_vehicles
from api.crews import get_crews
from api.routes import router as routes_router
from storage.history import init_db as init_history_db
from storage.routes import init_db as init_routes_db
import scheduler
from agent.planner import generate_basic_schedule

logger = logging.getLogger(__name__)

__all__ = ["app"]

app.include_router(routes_router)


@app.on_event("startup")
async def startup() -> None:
    await init_http_client()
    init_history_db()
    init_routes_db()
    scheduler.start()

    # Temporary MVP logic - replace with scheduler + cronjob later.
    logger.info("Starting basic planning on startup")

    async def _run_basic_planning() -> None:
        try:
            await generate_basic_schedule()
        except Exception:
            logger.exception("Error running basic planning on startup")

    asyncio.create_task(_run_basic_planning())


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
