"""TaskResult type for Open Robot Brain.

A **task result** aggregates the outcome of executing a :class:`Task`:

- the plan that was produced (if any),
- the per-skill results,
- the overall task status,
- an optional human-readable message and payload.

This type is produced by the executor, not by the planner or skills.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import Field

from orb_types.base import ORBModel, Timestamp
from orb_types.ids import TaskId
from orb_types.plan import Plan
from orb_types.skill import SkillResult

# ─── Enums ───────────────────────────────────────────────────────────────


class TaskResultStatus(StrEnum):
    """Final status of a task execution."""

    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    NOT_PLANNED = "not_planned"
    """No plan was produced (planner failed or returned nothing)."""


# ─── TaskResult ──────────────────────────────────────────────────────────


class TaskResult(ORBModel):
    """Aggregated outcome of executing a task.

    Fields
    ------
    task_id:
        The task this result refers to.
    status:
        Final task status.
    timestamp:
        When the result was produced.
    plan:
        The plan that was executed, if any.
    skill_results:
        Ordered tuple of per-skill results.
    message:
        Optional human-readable message.
    payload:
        Optional structured result data.
    """

    task_id: TaskId
    status: TaskResultStatus
    timestamp: Timestamp
    plan: Plan | None = None
    skill_results: tuple[SkillResult, ...] = ()
    message: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


__all__ = [
    "TaskResult",
    "TaskResultStatus",
]
