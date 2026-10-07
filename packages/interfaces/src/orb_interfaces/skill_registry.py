"""Skill registry protocol.

A skill registry maps :class:`SkillId` to executable skills and provides
a uniform way to run them against the current world.

This module defines only the **protocol**. Concrete registries and skill
implementations live in ``brain/skills/``.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from orb_types import Skill, SkillId, SkillResult, WorldState


@runtime_checkable
class SkillRegistry(Protocol):
    """Protocol for skill lookup and execution."""

    def get(self, skill_id: SkillId) -> Skill | None:
        """Return the skill with the given ID, or ``None``."""
        ...

    def has(self, skill_id: SkillId) -> bool:
        """Return whether the registry knows the given skill."""
        ...

    def execute(
        self,
        skill_id: SkillId,
        parameters: dict[str, Any],
        world: WorldState,
    ) -> SkillResult:
        """Execute the skill with the given parameters against the world.

        Implementations must not raise for expected failures (missing
        preconditions, unreachable object, …): they must return a
        :class:`SkillResult` with a non-success status. They may raise for
        programming errors (unknown skill ID, malformed parameters).
        """
        ...


__all__ = ["SkillRegistry"]
