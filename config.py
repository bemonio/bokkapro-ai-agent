"""Loads environment configuration and defines global constants."""

import os
from dotenv import load_dotenv

load_dotenv()

BOKKA_API_BASE_URL: str = os.getenv("BOKKA_API_BASE_URL", "https://api.bokkapro.com")
HTTP_TIMEOUT_SECONDS: float = float(os.getenv("HTTP_TIMEOUT_SECONDS", "15"))
HTTP_RETRY_ATTEMPTS: int = int(os.getenv("HTTP_RETRY_ATTEMPTS", "3"))
HTTP_RETRY_BACKOFF_SECONDS: float = float(
    os.getenv("HTTP_RETRY_BACKOFF_SECONDS", "0.5")
)
DEPOT_LAT: float = float(os.getenv("DEPOT_LAT", "0"))
DEPOT_LON: float = float(os.getenv("DEPOT_LON", "0"))
PLANNING_HORIZON_START: str = os.getenv("PLANNING_HORIZON_START", "08:00")
PLANNING_HORIZON_END: str = os.getenv("PLANNING_HORIZON_END", "18:00")
REPORTING_POST_URL: str = os.getenv(
    "REPORTING_POST_URL", "https://api.example.com/route_plans"
)
STOPS_API_URL: str = os.getenv("STOPS_API_URL", "https://api.example.com/stops")
AUTH_TOKEN: str = os.getenv("AUTH_TOKEN", "")
DAILY_SCHEDULE_CRON: str = os.getenv("DAILY_SCHEDULE_CRON", "0 7 * * *")
PLAN_HISTORY_SIZE: int = int(os.getenv("PLAN_HISTORY_SIZE", "10"))
WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "")

# Planner settings
USE_MULTI_DEPOT: bool = os.getenv("USE_MULTI_DEPOT", "false").lower() == "true"
AVERAGE_SPEED_KMPH: int = int(os.getenv("AVERAGE_SPEED_KMPH", "40"))
SERVICE_TIME_MINUTES_DEFAULT: int = int(os.getenv("SERVICE_TIME_MINUTES_DEFAULT", "5"))
SOLVER_TIMEOUT_SECONDS: int = int(os.getenv("SOLVER_TIMEOUT_SECONDS", "30"))
SOLVER_FIRST_SOLUTION: str = os.getenv("SOLVER_FIRST_SOLUTION", "PATH_CHEAPEST_ARC")
SOLVER_METAHEURISTIC: str = os.getenv("SOLVER_METAHEURISTIC", "GUIDED_LOCAL_SEARCH")
