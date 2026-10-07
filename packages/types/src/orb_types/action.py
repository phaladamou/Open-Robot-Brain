"""Action types for Open Robot Brain.

An **action** is a *semantic* request from the brain to the embodiment layer
(e.g. ``grasp(object_id="cup_01")``). It is **not** a low-level motor command.

Design
------
- ``Action`` carries a ``name`` and free-form ``parameters``. Validation of
  parameters is the responsibility of the :class:`SkillRegistry` (not here).
- ``ActionSpec`` is the *template* (name + parameter schema) used to validate
  actions and to describe what the brain can ask for.
- ``ActionResult`` reports the outcome of a dispatched action.
- All types are immutable and timestamped.

This separation is what lets the same brain talk to different robots: the
embodiment layer translates semantic actions into body-specific commands.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Any

from pydantic import Field

from orb_types.base import ORBModel, Timestamp
from orb_types.ids import ActionId, SkillId

# ─── Enums ───────────────────────────────────────────────────────────────


class ActionStatus(StrEnum):
    """Lifecycle status of an action."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ─── Action ──────────────────────────────────────────────────────────────


class Action(ORBModel):
    """A semantic action request from the brain to the embodiment layer.

    Fields
    ------
    action_id:
        Unique identifier for this action.
    name:
        Semantic name (e.g. ``"grasp"``, ``"navigate_to"``, ``"pick"``).
    parameters:
        Free-form parameter bag. Validation is delegated to the skill that
        owns this action (via :class:`ActionSpec`).
    skill_id:
        Optional reference to the skill that produced this action.
    status:
        Lifecycle status (defaults to ``PENDING``).
    timestamp:
        When the action was created.
    """

    action_id: ActionId
    name: Annotated[str, Field(min_length=1)]
    parameters: dict[str, Any] = Field(default_factory=dict)
    skill_id: SkillId | None = None
    status: ActionStatus = ActionStatus.PENDING
    timestamp: Timestamp

    def is_terminal(self) -> bool:
        """Return whether the action is in a terminal state."""
        return self.status in (
            ActionStatus.SUCCEEDED,
            ActionStatus.FAILED,
            ActionStatus.CANCELLED,
        )


# ─── ActionSpec ──────────────────────────────────────────────────────────


class ActionSpec(ORBModel):
    """A template describing an action the brain can request.

    ``parameters`` is a mapping of parameter name to a JSON-schema-like
    description. This is intentionally loose in v0.1 — formal JSON Schema
    validation will be added later.
    """

    name: Annotated[str, Field(min_length=1)]
    description: str = ""
    parameters: dict[str, Any] = Field(default_factory=dict)
    required: tuple[str, ...] = ()


# ─── ActionResult ────────────────────────────────────────────────────────


class ActionResult(ORBModel):
    """Outcome of a dispatched action.

    Fields
    ------
    action_id:
        The action this result refers to.
    status:
        Final status (must be terminal in practice).
    timestamp:
        When the result was produced.
    message:
        Optional human-readable message (e.g. failure reason).
    payload:
        Optional structured result data.
    """

    action_id: ActionId
    status: ActionStatus
    timestamp: Timestamp
    message: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


__all__ = [
    "Action",
    "ActionResult",
    "ActionSpec",
    "ActionStatus",
]
