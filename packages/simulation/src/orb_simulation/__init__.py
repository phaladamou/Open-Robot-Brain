"""orb-simulation — simulation backends for Open Robot Brain.

Public API is re-exported here.
"""

from orb_simulation.environments import (
    empty,
    kitchen_simple,
    table_with_cube,
    table_with_cubes,
)
from orb_simulation.mock import MockSimulator
from orb_simulation.scenarios import SCENARIOS, get_scenario

__all__ = [
    "SCENARIOS",
    "MockSimulator",
    "empty",
    "get_scenario",
    "kitchen_simple",
    "table_with_cube",
    "table_with_cubes",
]
