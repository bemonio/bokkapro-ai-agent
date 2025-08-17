"""FastAPI endpoints for interacting with the route agent."""

from fastapi import FastAPI

app = FastAPI(title="BokkaPro AI Agent")


@app.post("/agent/run")
async def run_agent() -> dict:
    """Trigger the route planning process."""
    # TODO: Implement interaction with RouteAgent.
    return {"status": "placeholder"}


@app.get("/agent/status")
async def agent_status() -> dict:
    """Retrieve the current status of the agent."""
    # TODO: Return real status information.
    return {"status": "idle"}
