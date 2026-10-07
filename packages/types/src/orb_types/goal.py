"""Goal types for Open Robot Brain.

A **goal** is a *desire*: a declarative statement of what should become true
in the world. Goals are produced from human instructions (natural language)
or from higher-level reasoning. They are **not** plans — turning a goal into
a sequence of skills is the planner's job.

Design
------
- A goal carries both:
  - a human-readable ``description`` (the natural-language intent), and
  - a structured ``kind`` + ``predicate`` + ``args`` (for the planner).
- Goals are immutable and timestamped.
- Goal status tracks the lifecycle from creation to outcome.

The ``Goal`` / ``Task`` separation mirrors the classical BDI model:
a *goal* is a desire; a *task* is a concrete commitment to achieve it.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Any

from pydantic import Field

from orb_types.base import ORBModel, Timestamp
from orb_types.ids import AgentId, GoalId, ObjectId

# ─── Enums ───────────────────────────────────────────────────────────────


class GoalKind(StrEnum):
    """Semantic category of a goal."""

    SPATIAL = "spatial"  # move to, place on, reach
    MANIPULATION = "manipulation"  # pick, place, open, close
    PERCEPTUAL = "perceptual"  # find, inspect, verify
    COMMUNICATION = "communication"  # speak, signal
    NAVIGATION = "navigation"  # go to a location
    COMPOSITE = "composite"  # combine multiple sub-goals
    OTHER = "other"


class GoalStatus(StrEnum):
    """Lifecycle status of a goal."""

    PENDING = "pending"
    ACTIVE = "active"
    ACHIEVED = "achieved"
    FAILED = "failed"
    ABANDONED = "abandoned"


# ─── Goal ────────────────────────────────────────────────────────────────


class Goal(ORBModel):
    """A declarative desire — what should become true.

    Fields
    ------
    goal_id:
        Unique identifier.
    description:
        Natural-language statement of the intent (e.g. ``"Pick up the red cup"``).
        This is what a human said, or what a higher-level reasoner produced.
    kind:
        Semantic category (see :class:`GoalKind`).
    predicate:
        Optional structured predicate for the planner (e.g. ``"holding"``).
    args:
        Optional arguments for the predicate (e.g. ``{"object_id": "cup_01"}``).
    target_object:
        Optional object this goal concerns.
    target_location:
        Optional location name this goal concerns.
    assigned_to:
        Optional agent this goal is assigned to.
    status:
        Current lifecycle status.
    created_at:
        When the goal was created.
    """

    goal_id: GoalId
    description: Annotated[str, Field(min_length=1)]
    kind: GoalKind = GoalKind.OTHER
    predicate: str | None = None
    args: dict[str, Any] = Field(default_factory=dict)
    target_object: ObjectId | None = None
    target_location: str | None = None
    assigned_to: AgentId | None = None
    status: GoalStatus = GoalStatus.PENDING
    created_at: Timestamp

    def is_terminal(self) -> bool:
        """Return whether the goal is in a terminal state."""
        return self.status in (
            GoalStatus.ACHIEVED,
            GoalStatus.FAILED,
            GoalStatus.ABANDONED,
        )


__all__ = [
    "Goal",
    "GoalKind",
    "GoalStatus",
]
