from fastapi import FastAPI

app = FastAPI()


@app.post("/agent/run")
def run_agent() -> dict[str, str]:
    return {"status": "scheduled"}


@app.get("/agent/status")
def agent_status() -> dict[str, str]:
    return {"status": "idle"}
