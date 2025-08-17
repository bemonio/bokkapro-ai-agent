"""Test cases for the Planner placeholder."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from agent.planner import Planner


def test_planner_instance() -> None:
    """Planner can be instantiated."""
    planner = Planner()
    assert planner is not None
