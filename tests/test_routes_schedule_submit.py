import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Column, String, Table, create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import api.routes as routes_module
import storage.routes as storage_routes


@pytest.mark.asyncio
async def test_submit_schedule(tmp_path, monkeypatch):
    db_path = tmp_path / "routes.db"

    # Prepare synchronous engine to create tables and seed data
    sync_engine = create_engine(f"sqlite:///{db_path}", future=True)
    metadata = storage_routes.Base.metadata
    Table("vehicles", metadata, Column("id", String, primary_key=True))
    Table("crews", metadata, Column("id", String, primary_key=True))
    Table("offices", metadata, Column("id", String, primary_key=True))
    Table("tasks", metadata, Column("id", String, primary_key=True))
    metadata.create_all(sync_engine)
    with sync_engine.begin() as conn:
        conn.execute(text("INSERT INTO vehicles(id) VALUES ('v1'), ('v2')"))
        conn.execute(text("INSERT INTO crews(id) VALUES ('c1'), ('c2')"))
        conn.execute(text("INSERT INTO offices(id) VALUES ('o1')"))
        conn.execute(text("INSERT INTO tasks(id) VALUES ('t1'), ('t2'), ('t3')"))

    # Patch API session to use async engine with the test DB
    async_engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}", future=True)
    TestSession = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)
    monkeypatch.setattr(routes_module, "engine", async_engine)
    monkeypatch.setattr(routes_module, "SessionLocal", TestSession)

    app = FastAPI()
    app.include_router(routes_module.router)
    client = TestClient(app)

    payload1 = {
        "date": "2025-08-17",
        "routes": [
            {
                "vehicle_id": "v1",
                "crew_id": "c1",
                "office_id": "o1",
                "tasks": [
                    {
                        "task_id": "t1",
                        "order": 1,
                        "estimated_start": "2025-08-17T08:00:00",
                        "estimated_end": "2025-08-17T08:20:00",
                    }
                ],
            }
        ],
    }

    resp1 = client.post("/routes/schedule/submit", json=payload1)
    assert resp1.status_code == 200
    assert resp1.json() == {"created": 1, "overwritten": 0}

    payload2 = {
        "date": "2025-08-17",
        "routes": [
            {
                "vehicle_id": "v1",
                "crew_id": "c1",
                "office_id": "o1",
                "tasks": [
                    {
                        "task_id": "t2",
                        "order": 1,
                        "estimated_start": "2025-08-17T09:00:00",
                        "estimated_end": "2025-08-17T09:20:00",
                    }
                ],
            },
            {
                "vehicle_id": "v2",
                "crew_id": "c2",
                "office_id": "o1",
                "tasks": [
                    {
                        "task_id": "t3",
                        "order": 1,
                        "estimated_start": "2025-08-17T10:00:00",
                        "estimated_end": "2025-08-17T10:20:00",
                    }
                ],
            },
        ],
    }

    resp2 = client.post("/routes/schedule/submit", json=payload2)
    assert resp2.status_code == 200
    assert resp2.json() == {"created": 1, "overwritten": 1}

    # verify that route for v1 now references task t2
    with sync_engine.connect() as conn:
        count_routes = conn.execute(text("SELECT COUNT(*) FROM routes")).scalar_one()
        assert count_routes == 2
        route_id_v1 = conn.execute(
            text("SELECT id FROM routes WHERE vehicle_id='v1'")
        ).scalar_one()
        task_for_v1 = conn.execute(
            text("SELECT task_id FROM route_task_links WHERE route_id=:rid"),
            {"rid": route_id_v1},
        ).scalar_one()
        assert task_for_v1 == "t2"
