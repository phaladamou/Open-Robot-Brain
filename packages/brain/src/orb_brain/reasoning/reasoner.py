"""Reasoner: judge whether a goal is well-formed, reachable, feasible.

v0.1 checks, in order:

1. **Well-formed**: the goal has a non-empty description and a predicate
   or a target (object or location).
2. **Reachable**: if the goal references a target object, that object must
   exist in the current world.
3. **Feasible**: the goal requires certain capabilities (derived from its
   kind and predicate); the embodiment must expose them.

The reasoner does **not** plan. It returns a :class:`ReasoningResult`.
"""

from __future__ import annotations

from orb_interfaces import CapabilityProvider
from orb_types import (
    CapabilityId,
    Goal,
    GoalKind,
    ReasoningResult,
    WorldState,
)

# ─── Mapping kind/predicate → required capabilities ──────────────────────

_REQUIRED_CAPABILITIES: dict[tuple[GoalKind, str | None], tuple[str, ...]] = {
    (GoalKind.MANIPULATION, "pick"): ("can_grasp", "can_lift"),
    (GoalKind.MANIPULATION, "place"): ("can_grasp", "can_lift"),
    (GoalKind.MANIPULATION, "open"): ("can_grasp",),
    (GoalKind.MANIPULATION, "close"): ("can_grasp",),
    (GoalKind.NAVIGATION, "at"): ("can_navigate",),
    (GoalKind.PERCEPTUAL, "known"): ("can_see",),
}


def _required_for(goal: Goal) -> tuple[str, ...]:
    return _REQUIRED_CAPABILITIES.get((goal.kind, goal.predicate), ())


# ─── Reasoner ────────────────────────────────────────────────────────────


class Reasoner:
    """Judge whether a goal is well-formed, reachable, and feasible.

    Parameters
    ----------
    capabilities:
        Provider of the embodiment's :class:`CapabilitySet`.
    """

    def __init__(self, capabilities: CapabilityProvider) -> None:
        self._capabilities = capabilities

    def reason(self, goal: Goal, world: WorldState) -> ReasoningResult:
        """Return a :class:`ReasoningResult` for ``goal`` in ``world``."""
        errors: list[str] = []
        warnings: list[str] = []

        self._check_well_formed(goal, errors)
        self._check_reachable(goal, world, errors, warnings)
        self._check_feasible(goal, errors)

        return ReasoningResult(
            goal_id=goal.goal_id,
            ok=not errors,
            errors=tuple(errors),
            warnings=tuple(warnings),
        )

    # ─── Checks ─────────────────────────────────────────────────────────

    def _check_well_formed(self, goal: Goal, errors: list[str]) -> None:
        if not goal.description:
            errors.append("goal has empty description")
        if goal.predicate is None and not goal.args:
            errors.append("goal has no predicate and no arguments")

    def _check_reachable(
        self,
        goal: Goal,
        world: WorldState,
        errors: list[str],
        warnings: list[str],
    ) -> None:
        if goal.target_object is not None and world.get_object(goal.target_object) is None:
            errors.append(f"target object {goal.target_object!r} not found in world")

        # A target location may be declared either as a structured field on
        # the goal or inside its arguments. Both are legitimate; check both.
        location = goal.target_location or goal.args.get("location")
        if location is not None and world.get_location(location) is None:
            warnings.append(f"target location {location!r} not in world (proceeding)")

    def _check_feasible(self, goal: Goal, errors: list[str]) -> None:
        required = _required_for(goal)
        if not required:
            return
        caps = self._capabilities.capabilities()
        for cap_name in required:
            if not caps.has(CapabilityId(cap_name)):
                errors.append(f"missing capability {cap_name!r}")


__all__ = ["Reasoner"]
