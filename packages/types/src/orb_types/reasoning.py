"""Reasoning types for Open Robot Brain.

These types capture the **outcome of reasoning**: whether a goal is
well-formed, reachable, and feasible given the current world and the
capabilities of the current embodiment.

Reasoning does **not** plan. It only judges. Planning is the planner's job.
"""

from __future__ import annotations

from orb_types.base import ORBModel
from orb_types.ids import GoalId


class ReasoningResult(ORBModel):
    """Structured outcome of reasoning about a goal.

    Fields
    ------
    goal_id:
        The goal that was reasoned about.
    ok:
        Whether the goal is well-formed, reachable, and feasible.
    errors:
        Blocking problems. If ``ok`` is ``True``, this is empty.
    warnings:
        Non-blocking remarks (e.g. low confidence, ambiguous reference).
    """

    goal_id: GoalId
    ok: bool
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def is_ok(self) -> bool:
        """Return whether reasoning succeeded with no errors."""
        return self.ok and not self.errors


__all__ = ["ReasoningResult"]
