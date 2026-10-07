"""In-memory skill registry.

The registry is the concrete implementation of the
:class:`~orb_interfaces.SkillRegistry` protocol. It:

- stores executable :class:`BaseSkill` instances by id,
- exposes their declarative :class:`~orb_types.Skill` descriptions,
- publishes ``SKILL_STARTED`` and ``SKILL_FINISHED`` events on the bus
  for every execution.
"""

from __future__ import annotations

from typing import Any

import structlog
from orb_runtime import EventBus
from orb_types import (
    Event,
    EventId,
    EventKind,
    EventSeverity,
    Skill,
    SkillId,
    SkillResult,
    SkillStatus,
    WorldState,
    new_id,
    utc_now,
)

from orb_brain.skills.base import BaseSkill

logger = structlog.get_logger(__name__)


class InMemorySkillRegistry:
    """A simple, in-memory implementation of the ``SkillRegistry`` protocol.

    Parameters
    ----------
    bus:
        Event bus used to publish ``SKILL_STARTED`` and ``SKILL_FINISHED``.
    """

    def __init__(self, bus: EventBus) -> None:
        self._bus = bus
        self._skills: dict[SkillId, BaseSkill] = {}

    # ─── Registration ───────────────────────────────────────────────────

    def register(self, skill: BaseSkill) -> None:
        """Register a skill. Overwrites an existing one with the same id."""
        skill_id = skill.spec.skill_id
        self._skills[skill_id] = skill
        logger.info("skill.registered", skill_id=skill_id)

    def register_many(self, *skills: BaseSkill) -> None:
        """Register several skills in one call."""
        for skill in skills:
            self.register(skill)

    # ─── Lookup ─────────────────────────────────────────────────────────

    def get(self, skill_id: SkillId) -> Skill | None:
        """Return the declarative description of a skill, or ``None``."""
        skill = self._skills.get(skill_id)
        return skill.spec if skill is not None else None

    def get_executable(self, skill_id: SkillId) -> BaseSkill | None:
        """Return the executable skill instance, or ``None``."""
        return self._skills.get(skill_id)

    def has(self, skill_id: SkillId) -> bool:
        """Return whether the registry knows the given skill."""
        return skill_id in self._skills

    def skill_ids(self) -> tuple[SkillId, ...]:
        """Return all registered skill ids."""
        return tuple(self._skills.keys())

    # ─── Execution ──────────────────────────────────────────────────────

    def execute(
        self,
        skill_id: SkillId,
        parameters: dict[str, Any],
        world: WorldState,
    ) -> SkillResult:
        """Execute a skill and return its result.

        Publishes ``SKILL_STARTED`` before running and ``SKILL_FINISHED``
        after. Raises :class:`KeyError` for unknown skill ids (that is a
        programming error, not an expected failure).
        """
        skill = self._skills.get(skill_id)
        if skill is None:
            msg = f"unknown skill: {skill_id!r}"
            raise KeyError(msg)

        self._publish(
            kind=EventKind.SKILL_STARTED,
            skill_id=skill_id,
            payload={"parameters": dict(parameters)},
        )

        result = skill.run(parameters, world)

        self._publish(
            kind=EventKind.SKILL_FINISHED,
            skill_id=skill_id,
            severity=(
                EventSeverity.INFO
                if result.status is SkillStatus.SUCCEEDED
                else EventSeverity.WARNING
            ),
            payload={
                "status": result.status,
                "message": result.message,
            },
        )
        return result

    # ─── Internal ───────────────────────────────────────────────────────

    def _publish(
        self,
        *,
        kind: EventKind,
        skill_id: SkillId,
        payload: dict[str, Any],
        severity: EventSeverity = EventSeverity.INFO,
    ) -> None:
        self._bus.publish(
            Event(
                event_id=EventId(new_id("evt")),
                kind=kind,
                timestamp=utc_now(),
                source="skill_registry",
                severity=severity,
                payload={"skill_id": skill_id, **payload},
            )
        )


__all__ = ["InMemorySkillRegistry"]
