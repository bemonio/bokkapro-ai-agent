"""Entry point for launching the FastAPI server and initializing the agent."""

import logging

from fastapi import FastAPI

from api.api import app as api_app


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # TODO: Initialize RouteAgent and dependencies here.
    logging.info("Creating FastAPI app")
    return api_app


app = create_app()
