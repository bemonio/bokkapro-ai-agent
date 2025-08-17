from fastapi import FastAPI, HTTPException
from planner.service import build_today_plan, publish_plan, get_latest_plan
from planner.dtos import PlanResultDTO

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


@app.get("/agent/status")
def agent_status() -> dict[str, str]:
    return {"status": "idle"}
