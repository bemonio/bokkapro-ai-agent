"""Launches FastAPI server and initializes the route planning agent."""

import logging

from api.api import app

logger = logging.getLogger(__name__)


def init_agent() -> None:
    """Initialize agent components on startup."""
    # TODO: Set up RouteAgent and Scheduler
    pass


if __name__ == "__main__":
    # Placeholder server startup
    import uvicorn

    init_agent()
    uvicorn.run(app, host="0.0.0.0", port=8000)
