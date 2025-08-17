import logging
import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from planner.service import build_today_plan, publish_plan
import config

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def _run_job() -> None:
    start = time.perf_counter()
    plan = await build_today_plan()
    await publish_plan(plan)
    duration = time.perf_counter() - start
    vehicles = len(plan.vehicle_plans)
    tasks = sum(len(v.tasks_order) for v in plan.vehicle_plans)
    unscheduled = len(plan.unscheduled)
    logger.info(
        "plan built: vehicles=%s tasks=%s unscheduled=%s duration=%.2fs",
        vehicles,
        tasks,
        unscheduled,
        duration,
    )


def start() -> None:
    scheduler.add_job(_run_job, CronTrigger.from_crontab(config.DAILY_SCHEDULE_CRON))
    scheduler.start()


async def shutdown() -> None:
    await scheduler.shutdown()
