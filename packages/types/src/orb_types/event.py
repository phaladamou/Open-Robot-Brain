"""Event types for Open Robot Brain.

An **event** is a timestamped notification that *something happened*. Events
are the nervous system of ORB: they flow through the runtime bus, are
consumed by the world model, logged for debugging, and (later) replayed for
learning.

Design
------
- Events are **immutable** and **timestamped**.
- ``kind`` is a typed enum for known events + ``CUSTOM`` for extension.
- ``severity`` follows the Python logging convention (DEBUG…CRITICAL).
- ``correlation_id`` is a free-form string used to trace causal chains
  (a task, a session, a parent event, etc.).
- This module defines **only the type**. The bus, queue, and handlers live
  in ``runtime/events/`` — ``orb_types`` stays pure data.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Any

from pydantic import Field

from orb_types.base import ORBModel, Timestamp
from orb_types.ids import EventId

# ─── Enums ───────────────────────────────────────────────────────────────


class EventSeverity(StrEnum):
    """Severity of an event, aligned with the Python logging convention."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class EventKind(StrEnum):
    """Category of an event.

    Known kinds are enumerated for rigor. ``CUSTOM`` is used with an
    additional ``kind_label`` in the payload for anything not yet modeled.
    """

    # Perception
    PERCEPTION_RECEIVED = "perception.received"
    OBSERVATION_CREATED = "observation.created"

    # World model
    WORLD_UPDATED = "world.updated"
    OBJECT_ADDED = "world.object_added"
    OBJECT_REMOVED = "world.object_removed"

    # Reasoning & planning
    GOAL_CREATED = "goal.created"
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    PLAN_CREATED = "plan.created"
    PLAN_FAILED = "plan.failed"

    # Skills & actions
    SKILL_STARTED = "skill.started"
    SKILL_FINISHED = "skill.finished"
    ACTION_DISPATCHED = "action.dispatched"
    ACTION_COMPLETED = "action.completed"
    ACTION_FAILED = "action.failed"

    # Runtime
    RUNTIME_STARTED = "runtime.started"
    RUNTIME_STOPPED = "runtime.stopped"
    SCHEDULER_TICK = "scheduler.tick"

    # Safety
    SAFETY_VIOLATION = "safety.violation"
    EMERGENCY_STOP = "safety.emergency_stop"

    # Extension
    CUSTOM = "custom"


# ─── Event ───────────────────────────────────────────────────────────────


class Event(ORBModel):
    """An immutable, timestamped notification.

    Fields
    ------
    event_id:
        Unique identifier.
    kind:
        Event category (see :class:`EventKind`).
    timestamp:
        When the event occurred.
    source:
        Producer of the event (``"perception"``, ``"planner"``, ``"runtime"``,
        ``"safety"``, …).
    severity:
        Severity level.
    payload:
        Free-form event data.
    correlation_id:
        Optional identifier linking this event to a causal chain (a task, a
        session, a parent event, etc.).
    """

    event_id: EventId
    kind: EventKind
    timestamp: Timestamp
    source: Annotated[str, Field(min_length=1)] = "runtime"
    severity: EventSeverity = EventSeverity.INFO
    payload: dict[str, Any] = Field(default_factory=dict)
    correlation_id: str | None = None


__all__ = [
    "Event",
    "EventKind",
    "EventSeverity",
]
