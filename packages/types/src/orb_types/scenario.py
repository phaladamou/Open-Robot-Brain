"""Scenario type for Open Robot Brain.

A **scenario** is a fully-specified, reproducible situation:

- a name,
- an initial world,
- a natural-language instruction (what the human asks),
- optionally, the robot identifier to use,
- free-form metadata (tags, version, expected outcome, …).

Scenarios are the **unit of evaluation**: a benchmark is a collection of
scenarios, a demo is a scenario, a regression test replays a scenario.

The type is pure data — building it is the simulation layer's job.
"""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import Field

from orb_types.base import ORBModel
from orb_types.ids import RobotId
from orb_types.world_state import WorldState


class Scenario(ORBModel):
    """A reproducible situation: world + instruction.

    Fields
    ------
    name:
        Stable identifier (e.g. ``"pick_red_cube"``).
    instruction:
        Natural-language instruction the brain will parse.
    world:
        Initial world state.
    robot_id:
        Optional robot identifier (defaults to ``"mock"`` at use site).
    metadata:
        Free-form annotations (tags, expected outcome, version, …).
    """

    name: Annotated[str, Field(min_length=1)]
    instruction: Annotated[str, Field(min_length=1)]
    world: WorldState
    robot_id: RobotId | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


__all__ = ["Scenario"]
