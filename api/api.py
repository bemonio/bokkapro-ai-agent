"""FastAPI endpoints to manually trigger planning and check status."""

from fastapi import FastAPI

app = FastAPI()


@app.post("/agent/run")
def run_agent() -> dict:
    """Trigger manual re-planning."""
    # TODO: Integrate with RouteAgent
    return {"status": "scheduled"}


@app.get("/agent/status")
def agent_status() -> dict:
    """Return current agent status."""
    # TODO: Return real status
    return {"status": "idle"}
