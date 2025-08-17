"""Example test case for the planner module."""

import sys
from pathlib import Path

# Allow imports from project root
sys.path.append(str(Path(__file__).resolve().parents[1]))

from agent.planner import Planner


def test_planner_placeholder() -> None:
    """Ensure the Planner.plan method can be invoked."""
    planner = Planner()
    planner.plan()
    assert True
