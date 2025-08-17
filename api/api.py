import hashlib
import hmac
from fastapi import FastAPI, HTTPException, Request
from planner.service import (
    build_today_plan,
    publish_plan,
    get_latest_plan,
    replan_incremental,
    get_plan_metrics,
)
from planner.dtos import PlanResultDTO
from storage.history import get_recent_plans
import config

app = FastAPI()


@app.post("/agent/run")
async def run_agent() -> dict[str, int]:
    plan = await build_today_plan()
    await publish_plan(plan)
    vehicles = len(plan.vehicle_plans)
    tasks = sum(len(v.tasks_order) for v in plan.vehicle_plans)
    unscheduled = len(plan.unscheduled)
    return {"vehicles": vehicles, "tasks": tasks, "unscheduled": unscheduled}


@app.get("/agent/plan/preview")
async def plan_preview() -> PlanResultDTO:
    plan = get_latest_plan()
    if plan is None:
        raise HTTPException(status_code=404)
    return plan


@app.get("/agent/plan/metrics")
async def plan_metrics() -> dict[str, float | int]:
    metrics = get_plan_metrics()
    if metrics is None:
        raise HTTPException(status_code=404)
    return metrics


@app.get("/agent/status")
def agent_status() -> dict[str, str]:
    return {"status": "idle"}


async def _verify_signature(request: Request) -> bytes:
    body = await request.body()
    signature = request.headers.get("X-Signature")
    expected = hashlib.sha256(
        (config.WEBHOOK_SECRET + body.decode()).encode()
    ).hexdigest()
    if not signature or not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=401)
    return body


@app.post("/webhooks/pickup_created")
async def pickup_created(request: Request) -> dict[str, object]:
    await _verify_signature(request)
    await replan_incremental()
    return {"status": "ok", "replanned": True}


@app.post("/webhooks/vehicle_status_changed")
async def vehicle_status_changed(request: Request) -> dict[str, object]:
    await _verify_signature(request)
    await replan_incremental()
    return {"status": "ok", "replanned": True}


@app.get("/agent/plan/history")
def plan_history(limit: int = 5) -> list[PlanResultDTO]:
    return get_recent_plans(limit)
