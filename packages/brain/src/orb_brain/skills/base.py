"""Base class for executable skills.

See :mod:`orb_brain.skills` for the design rationale.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from orb_types import Skill, SkillResult, SkillStatus, WorldState, utc_now


class BaseSkill(ABC):
    """Abstract base for executable skills.

    Subclasses must:

    - set :attr:`_skill` (a declarative :class:`~orb_types.Skill`),
    - implement :meth:`run`.

    The public :attr:`spec` property exposes the declarative description
    so the registry can present it to external callers (SDK, dashboard).
    """

    #: Declarative description, set by subclasses.
    _skill: Skill

    @property
    def spec(self) -> Skill:
        """The declarative description of this skill."""
        return self._skill

    @abstractmethod
    def run(self, parameters: dict[str, Any], world: WorldState) -> SkillResult:
        """Execute the skill.

        Parameters
        ----------
        parameters:
            Parameters provided by the plan step.
        world:
            Current world state.

        Returns
        -------
        SkillResult
            Never raises for expected failures; returns a ``FAILED``
            result instead.
        """
        ...

    # ─── Helpers for subclasses ─────────────────────────────────────────

    def _success(
        self,
        *,
        message: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> SkillResult:
        return SkillResult(
            skill_id=self._skill.skill_id,
            status=SkillStatus.SUCCEEDED,
            timestamp=utc_now(),
            message=message,
            payload=payload or {},
        )

    def _failure(
        self,
        *,
        message: str,
        payload: dict[str, Any] | None = None,
    ) -> SkillResult:
        return SkillResult(
            skill_id=self._skill.skill_id,
            status=SkillStatus.FAILED,
            timestamp=utc_now(),
            message=message,
            payload=payload or {},
        )


__all__ = ["BaseSkill"]
