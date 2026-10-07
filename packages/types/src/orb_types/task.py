"""Task types for Open Robot Brain.

A **task** is a concrete commitment to achieve a :class:`Goal`. It carries
execution context: who owns it, its status, and a history of events.

Where a goal is *"pick the red cup"*, a task is *"attempt to pick the red
cup, right now, with this robot, and record what happened"*.

Design
------
- Immutable; updates are produced by replacement (``model_copy(update=...)``).
- ``history`` is a tuple of opaque event payloads (dicts) for v0.1. A richer
  ``TaskEvent`` type may replace it later.
- ``TaskStatus`` is intentionally orthogonal to ``GoalStatus`` — a task can
  fail while the goal remains pending (retry), or succeed while the goal is
  already achieved by another task.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import Field

from orb_types.base import ORBModel, Timestamp
from orb_types.goal import Goal
from orb_types.ids import AgentId, RobotId, TaskId

# ─── Enums ───────────────────────────────────────────────────────────────


class TaskStatus(StrEnum):
    """Lifecycle status of a task."""

    CREATED = "created"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ─── TaskContext ─────────────────────────────────────────────────────────


class TaskContext(ORBModel):
    """Execution context of a task.

    Captures *where* and *with whom* a task is being executed. This keeps
    :class:`Task` focused on lifecycle, and the context reusable.
    """

    robot_id: RobotId | None = None
    agent_id: AgentId | None = None
    location: str | None = None
    tags: tuple[str, ...] = ()


# ─── Task ────────────────────────────────────────────────────────────────


class Task(ORBModel):
    """A concrete commitment to achieve a goal.

    Fields
    ------
    task_id:
        Unique identifier.
    goal:
        The goal this task is committed to achieving.
    status:
        Current lifecycle status.
    context:
        Execution context (robot, agent, location, tags).
    created_at:
        When the task was created.
    updated_at:
        When the task was last updated.
    history:
        Immutable tuple of opaque event payloads (append-only).
    """

    task_id: TaskId
    goal: Goal
    status: TaskStatus = TaskStatus.CREATED
    context: TaskContext = Field(default_factory=TaskContext)
    created_at: Timestamp
    updated_at: Timestamp
    history: tuple[dict[str, Any], ...] = ()

    def is_terminal(self) -> bool:
        """Return whether the task is in a terminal state."""
        return self.status in (
            TaskStatus.SUCCEEDED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED,
        )

    def with_status(self, status: TaskStatus, *, now: Timestamp) -> Task:
        """Return a copy with the given status, updating ``updated_at``."""
        return self.model_copy(update={"status": status, "updated_at": now})

    def with_event(self, event: dict[str, Any], *, now: Timestamp) -> Task:
        """Return a copy with an appended history event, updating ``updated_at``."""
        return self.model_copy(update={"history": (*self.history, event), "updated_at": now})


__all__ = [
    "Task",
    "TaskContext",
    "TaskStatus",
]
