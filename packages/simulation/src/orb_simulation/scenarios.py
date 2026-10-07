"""Named scenarios for v0.1.

A scenario bundles an environment with an instruction. Scenarios are the
**unit of evaluation**: a benchmark is a set of scenarios, a demo is a
scenario, a regression test replays a scenario.

Usage
-----
>>> from orb_simulation.scenarios import get_scenario, SCENARIOS
>>> s = get_scenario("pick_red_cube")
>>> s.instruction
'pick the red cube'
"""

from __future__ import annotations

from collections.abc import Callable

from orb_types import RobotId, Scenario

from orb_simulation.environments import (
    kitchen_simple,
    table_with_cube,
    table_with_cubes,
)

# ─── Builders ────────────────────────────────────────────────────────────


def _pick_red_cube() -> Scenario:
    return Scenario(
        name="pick_red_cube",
        instruction="pick the red cube",
        world=table_with_cube(color="red"),
        robot_id=RobotId("mock"),
        metadata={"kind": "pick", "difficulty": "easy"},
    )


def _pick_blue_cube() -> Scenario:
    return Scenario(
        name="pick_blue_cube",
        instruction="pick the blue cube",
        world=table_with_cube(color="blue"),
        robot_id=RobotId("mock"),
        metadata={"kind": "pick", "difficulty": "easy"},
    )


def _place_cube_on_table() -> Scenario:
    world = table_with_cube(color="red")
    return Scenario(
        name="place_cube_on_table",
        instruction="place the red cube on the table",
        world=world,
        robot_id=RobotId("mock"),
        metadata={"kind": "place", "difficulty": "medium"},
    )


def _open_drawer() -> Scenario:
    world = kitchen_simple()
    return Scenario(
        name="open_drawer",
        instruction="open the drawer",
        world=world,
        robot_id=RobotId("mock"),
        metadata={"kind": "open", "difficulty": "medium"},
    )


def _pick_cube_among_many() -> Scenario:
    world = table_with_cubes("red", "blue", "green")
    return Scenario(
        name="pick_cube_among_many",
        instruction="pick the blue cube",
        world=world,
        robot_id=RobotId("mock"),
        metadata={"kind": "pick", "difficulty": "hard"},
    )


# ─── Registry ────────────────────────────────────────────────────────────

_SCENARIOS: dict[str, Callable[[], Scenario]] = {
    "pick_red_cube": _pick_red_cube,
    "pick_blue_cube": _pick_blue_cube,
    "place_cube_on_table": _place_cube_on_table,
    "open_drawer": _open_drawer,
    "pick_cube_among_many": _pick_cube_among_many,
}

#: Names of all known scenarios.
SCENARIOS: tuple[str, ...] = tuple(sorted(_SCENARIOS.keys()))


def get_scenario(name: str) -> Scenario:
    """Build and return the scenario with the given name.

    Raises
    ------
    KeyError
        If the scenario name is unknown.
    """
    if name not in _SCENARIOS:
        msg = f"unknown scenario: {name!r} (known: {', '.join(SCENARIOS)})"
        raise KeyError(msg)
    return _SCENARIOS[name]()


__all__ = ["SCENARIOS", "get_scenario"]
