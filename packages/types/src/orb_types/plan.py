"""Plan types for Open Robot Brain.

A **plan** is a structured sequence of steps produced by the planner from
a goal. A step names a skill and its parameters. A plan is purely
declarative — it does not execute anything.

Design
------
- A plan is tied to a goal (``goal_id``).
- Steps are ordered. The executor runs them sequentially in v0.1.
- ``PlanStatus`` tracks the plan's lifecycle as the executor works
  through it.
- A plan is immutable. Progress is reported via :class:`TaskResult`.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Any

from pydantic import Field

from orb_types.base import ORBModel, Timestamp
from orb_types.ids import GoalId, PlanId, SkillId

# ─── Enums ───────────────────────────────────────────────────────────────


class PlanStatus(StrEnum):
    """Lifecycle status of a plan."""

    CREATED = "created"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ─── PlanStep ────────────────────────────────────────────────────────────


class PlanStep(ORBModel):
    """A single step in a plan.

    A step is a **request to run a skill** with given parameters. It is
    declarative: no code, no side effects.

    Fields
    ------
    step_id:
        Stable identifier within the plan (e.g. ``"step_1"``).
    skill_id:
        The skill to run.
    parameters:
        Parameters to pass to the skill.
    description:
        Optional human-readable description of the step.
    """

    step_id: Annotated[str, Field(min_length=1)]
    skill_id: SkillId
    parameters: dict[str, Any] = Field(default_factory=dict)
    description: str = ""


# ─── Plan ────────────────────────────────────────────────────────────────


class Plan(ORBModel):
    """A structured plan produced by the planner from a goal.

    Fields
    ------
    plan_id:
        Unique identifier.
    goal_id:
        The goal this plan is intended to achieve.
    steps:
        Ordered tuple of steps. May be empty (e.g. trivial goal).
    status:
        Lifecycle status.
    created_at:
        When the plan was produced.
    """

    plan_id: PlanId
    goal_id: GoalId
    steps: tuple[PlanStep, ...] = ()
    status: PlanStatus = PlanStatus.CREATED
    created_at: Timestamp

    def is_empty(self) -> bool:
        """Return whether the plan has no steps."""
        return len(self.steps) == 0


__all__ = [
    "Plan",
    "PlanStatus",
    "PlanStep",
]
