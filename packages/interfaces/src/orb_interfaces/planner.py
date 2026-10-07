"""Planner protocol.

A planner turns a :class:`Goal` (given the current world) into a
:class:`Plan`. It is a pure function of goal + world, in principle —
implementations may be deterministic (HTN, PDDL) or learned (LLM-based,
RL).

This module defines only the **protocol**. Concrete planners live in
``brain/planning/``.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from orb_types import Goal, Plan, WorldState


@runtime_checkable
class Planner(Protocol):
    """Protocol for goal-to-plan planners."""

    def plan(self, goal: Goal, world: WorldState) -> Plan:
        """Return a plan for the given goal and world.

        Implementations may raise :class:`~orb_types.PlanningError` when no
        valid plan can be produced. Returning an empty plan is allowed and
        means "nothing to do".
        """
        ...


__all__ = ["Planner"]
