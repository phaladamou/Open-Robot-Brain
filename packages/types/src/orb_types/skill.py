"""Skill types for Open Robot Brain.

A **skill** is a reusable unit of behavior — a declarative description of a
task the brain knows how to perform (``pick``, ``place``, ``open_drawer``, …).

Design
------
- ``Skill`` is **pure data** (Pydantic, serializable). The *execution*
  logic lives in ``brain/skills/`` and is bound to a skill by ID.
- A skill declares:
  - its parameters (JSON-schema-like),
  - its **preconditions** (a tuple of :class:`Predicate`),
  - its **postconditions** (a tuple of :class:`Predicate`),
  - the **capabilities** it requires from the embodiment.
- ``SkillResult`` aggregates the outcome of all actions a skill dispatched.

This design keeps the brain body-agnostic: skills are contracts, not code.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Any

from pydantic import Field

from orb_types.action import ActionResult
from orb_types.base import ORBModel, Timestamp
from orb_types.ids import CapabilityId, SkillId

# ─── Enums ───────────────────────────────────────────────────────────────


class SkillStatus(StrEnum):
    """Lifecycle status of a skill execution."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    RECOVERED = "recovered"
    CANCELLED = "cancelled"


# ─── Predicate ───────────────────────────────────────────────────────────


class Predicate(ORBModel):
    """A structured predicate used for pre/postconditions.

    ``name`` is the predicate's identifier (e.g. ``"reachable"``,
    ``"holding"``). ``args`` are its parameters. The semantics of a
    predicate are defined by the consumer (planner, verifier, skill).

    This is intentionally PDDL-flavored but not committed to any specific
    planning language.
    """

    name: Annotated[str, Field(min_length=1)]
    args: dict[str, Any] = Field(default_factory=dict)


# ─── SkillSpec ───────────────────────────────────────────────────────────


class SkillSpec(ORBModel):
    """The declarative contract of a skill.

    Fields
    ------
    parameters:
        JSON-schema-like description of accepted parameters.
    required:
        Names of parameters that must be provided.
    preconditions:
        Predicates that must hold for the skill to be executable.
    postconditions:
        Predicates that are expected to hold after successful execution.
    required_capabilities:
        Capabilities the embodiment must expose for this skill to run.
    """

    parameters: dict[str, Any] = Field(default_factory=dict)
    required: tuple[str, ...] = ()
    preconditions: tuple[Predicate, ...] = ()
    postconditions: tuple[Predicate, ...] = ()
    required_capabilities: tuple[CapabilityId, ...] = ()


# ─── Skill ───────────────────────────────────────────────────────────────


class Skill(ORBModel):
    """A reusable unit of behavior, described as pure data.

    Fields
    ------
    skill_id:
        Stable identifier (e.g. ``pick``).
    name:
        Short human-readable name.
    description:
        What the skill does.
    spec:
        The declarative contract (see :class:`SkillSpec`).
    """

    skill_id: SkillId
    name: Annotated[str, Field(min_length=1)]
    description: str = ""
    spec: SkillSpec = Field(default_factory=SkillSpec)


# ─── SkillResult ─────────────────────────────────────────────────────────


class SkillResult(ORBModel):
    """Aggregated outcome of a skill execution.

    A skill may dispatch multiple :class:`Action` objects; this record
    aggregates their results and reports the skill-level outcome.

    Fields
    ------
    skill_id:
        The skill this result refers to.
    status:
        Skill-level status.
    timestamp:
        When the result was produced.
    action_results:
        Tuple of :class:`ActionResult` for the dispatched actions.
    message:
        Optional human-readable message.
    payload:
        Optional structured result data.
    """

    skill_id: SkillId
    status: SkillStatus
    timestamp: Timestamp
    action_results: tuple[ActionResult, ...] = ()
    message: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)

    def is_terminal(self) -> bool:
        """Return whether the skill is in a terminal state."""
        return self.status in (
            SkillStatus.SUCCEEDED,
            SkillStatus.FAILED,
            SkillStatus.RECOVERED,
            SkillStatus.CANCELLED,
        )


__all__ = [
    "Predicate",
    "Skill",
    "SkillResult",
    "SkillSpec",
    "SkillStatus",
]
