import sqlite3
from pathlib import Path

from planner.dtos import PlanResultDTO
import config

DB_PATH = Path(__file__).with_name("history.db")
_conn: sqlite3.Connection | None = None


def init_db() -> None:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(DB_PATH)
        _conn.execute(
            """
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                plan TEXT NOT NULL
            )
            """
        )
        _conn.commit()


def save_plan(plan: PlanResultDTO) -> None:
    if _conn is None:
        raise RuntimeError("DB not initialized")
    _conn.execute("INSERT INTO plans(plan) VALUES (?)", (plan.model_dump_json(),))
    _conn.commit()
    _conn.execute(
        "DELETE FROM plans WHERE id NOT IN (SELECT id FROM plans ORDER BY id DESC LIMIT ?)",
        (config.PLAN_HISTORY_SIZE,),
    )
    _conn.commit()


def get_recent_plans(limit: int) -> list[PlanResultDTO]:
    if _conn is None:
        raise RuntimeError("DB not initialized")
    cur = _conn.execute(
        "SELECT plan FROM plans ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    rows = cur.fetchall()
    return [PlanResultDTO.model_validate_json(r[0]) for r in rows]
