"""Strongly-typed identifiers for Open Robot Brain entities.

Every entity in ORB is referenced by a **typed** identifier, never by a
raw string. This prevents accidental cross-assignment (e.g. passing a
``RobotId`` where a ``SkillId`` is expected) and makes signatures
self-documenting.

Conventions
-----------
- IDs are **newtype-style** wrappers around :class:`str`.
- IDs are **immutable** and **hashable**.
- IDs must match ``^[a-z][a-z0-9_-]*$`` (lowercase, ``-`` and ``_`` allowed).
- Use :func:`new_id` to generate unique IDs with a given prefix.
"""

from __future__ import annotations

import re
import uuid
from typing import Annotated, NewType

from pydantic import AfterValidator, Field

# ─── Validation ──────────────────────────────────────────────────────────

_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_-]*$")


def _validate_id(value: str) -> str:
    if not _ID_PATTERN.match(value):
        msg = (
            f"Invalid ID {value!r}: must match {_ID_PATTERN.pattern} "
            "(lowercase, start with a letter, allow 'a-z 0-9 _ -')"
        )
        raise ValueError(msg)
    return value


_IdStr = Annotated[str, AfterValidator(_validate_id)]
"""A validated ID string. Used as the base for all typed IDs."""

# ─── Typed IDs ───────────────────────────────────────────────────────────

ObjectId = NewType("ObjectId", _IdStr)
"""Identifier for an object in the world (e.g. ``cup_01``)."""

AgentId = NewType("AgentId", _IdStr)
"""Identifier for an agent (robot, human, other) in the world."""

RobotId = NewType("RobotId", _IdStr)
"""Identifier for a physical or simulated robot."""

SkillId = NewType("SkillId", _IdStr)
"""Identifier for a registered skill (e.g. ``pick``)."""

CapabilityId = NewType("CapabilityId", _IdStr)
"""Identifier for a capability (e.g. ``can_grasp``)."""

TaskId = NewType("TaskId", _IdStr)
"""Identifier for a task instance."""

GoalId = NewType("GoalId", _IdStr)
"""Identifier for a goal."""

PlanId = NewType("PlanId", _IdStr)
"""Identifier for a plan."""

EventId = NewType("EventId", _IdStr)
"""Identifier for an event in the event bus."""

ActionId = NewType("ActionId", _IdStr)
"""Identifier for an action request."""

ObservationId = NewType("ObservationId", _IdStr)
"""Identifier for a single observation."""

WorldModelId = NewType("WorldModelId", _IdStr)
"""Identifier for a world model instance."""

MemoryId = NewType("MemoryId", _IdStr)
"""Identifier for a memory entry."""

# ─── Generator ───────────────────────────────────────────────────────────


def new_id(prefix: str) -> str:
    """Generate a new unique ID string with the given lowercase prefix.

    Example
    -------
    >>> new_id("obj")  # doctest: +SKIP
    'obj_a1b2c3d4'
    """
    if not _ID_PATTERN.match(prefix):
        msg = f"Invalid prefix {prefix!r}: must match {_ID_PATTERN.pattern}"
        raise ValueError(msg)
    suffix = uuid.uuid4().hex[:8]
    return f"{prefix}_{suffix}"


# Re-export Field for convenience in other modules importing from here.
__all__ = [
    "ActionId",
    "AgentId",
    "CapabilityId",
    "EventId",
    "Field",
    "GoalId",
    "MemoryId",
    "ObjectId",
    "ObservationId",
    "PlanId",
    "RobotId",
    "SkillId",
    "TaskId",
    "WorldModelId",
    "new_id",
]
