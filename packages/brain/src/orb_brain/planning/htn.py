"""Rule-based HTN planner.

See :mod:`orb_brain.planning` for the design rationale.

Decomposition rules are stored in :data:`_RULES`, mapping a goal predicate
to a *rule* — a callable that, given the goal and the world, returns a
tuple of :class:`PlanStep`. Rules may raise :class:`PlanningError` when
they cannot decompose the goal.
"""

from __future__ import annotations

from collections.abc import Callable

from orb_types import (
    Goal,
    ObjectId,
    Plan,
    PlanId,
    PlanningError,
    PlanStep,
    SkillId,
    WorldState,
    new_id,
    utc_now,
)

# ─── Helpers ─────────────────────────────────────────────────────────────


def _step(index: int, skill: str, **parameters: str) -> PlanStep:
    """Build a :class:`PlanStep` with a stable id."""
    return PlanStep(
        step_id=f"step_{index}",
        skill_id=SkillId(skill),
        parameters=dict(parameters),
    )


def _resolve_object(goal: Goal, world: WorldState) -> ObjectId:
    """Resolve the goal's target object to a concrete object id.

    Resolution order:

    1. If the goal already carries a ``target_object``, use it.
    2. Otherwise, match against the world using ``object_type`` and,
       when present, ``color``. The first matching object wins.
    3. If nothing matches, raise :class:`PlanningError`.
    """
    if goal.target_object is not None:
        if world.get_object(goal.target_object) is None:
            raise PlanningError(
                "target object not present in world",
                object_id=str(goal.target_object),
            )
        return goal.target_object

    object_type = goal.args.get("object_type")
    color = goal.args.get("color")

    if object_type is None and color is None:
        raise PlanningError(
            "goal has neither target_object nor object_type/color to resolve",
            goal_id=str(goal.goal_id),
        )

    for obj in world.objects:
        if object_type is not None and obj.type != object_type:
            continue
        if color is not None and obj.attributes.get("color") != color:
            continue
        return obj.object_id

    raise PlanningError(
        "no matching object in world",
        object_type=object_type,
        color=color,
    )


# ─── Rules ───────────────────────────────────────────────────────────────
#
# Each rule receives (goal, world) and returns a tuple[PlanStep, ...].


def _rule_pick(goal: Goal, world: WorldState) -> tuple[PlanStep, ...]:
    object_id = _resolve_object(goal, world)
    return (
        _step(1, "navigate_to", object_id=str(object_id)),
        _step(2, "reach", object_id=str(object_id)),
        _step(3, "grasp", object_id=str(object_id)),
        _step(4, "lift", object_id=str(object_id)),
    )


def _rule_place(goal: Goal, world: WorldState) -> tuple[PlanStep, ...]:
    object_id = _resolve_object(goal, world)
    target = goal.args.get("target")
    if target is None:
        raise PlanningError("place goal missing 'target' argument", goal_id=str(goal.goal_id))
    return (
        _step(1, "navigate_to", location=str(target)),
        _step(2, "reach", object_id=str(object_id)),
        _step(3, "release", object_id=str(object_id)),
    )


def _rule_navigate(goal: Goal, world: WorldState) -> tuple[PlanStep, ...]:
    location = goal.target_location or goal.args.get("location")
    if location is None:
        raise PlanningError("navigate goal missing location", goal_id=str(goal.goal_id))
    return (_step(1, "navigate_to", location=str(location)),)


def _rule_open(goal: Goal, world: WorldState) -> tuple[PlanStep, ...]:
    object_id = _resolve_object(goal, world)
    return (
        _step(1, "navigate_to", object_id=str(object_id)),
        _step(2, "reach", object_id=str(object_id)),
        _step(3, "pull", object_id=str(object_id)),
    )


def _rule_close(goal: Goal, world: WorldState) -> tuple[PlanStep, ...]:
    object_id = _resolve_object(goal, world)
    return (
        _step(1, "navigate_to", object_id=str(object_id)),
        _step(2, "reach", object_id=str(object_id)),
        _step(3, "push", object_id=str(object_id)),
    )


def _rule_find(goal: Goal, world: WorldState) -> tuple[PlanStep, ...]:
    # Perceptual goal: look around for the object. v0.1 uses a single
    # "inspect" step — the world model will handle the update when the
    # simulator produces the corresponding observation.
    return (_step(1, "inspect", target=str(goal.args.get("object_type", ""))),)


Rule = Callable[[Goal, WorldState], tuple[PlanStep, ...]]

_RULES: dict[str, Rule] = {
    "pick": _rule_pick,
    "place": _rule_place,
    "at": _rule_navigate,
    "open": _rule_open,
    "close": _rule_close,
    "known": _rule_find,
}


# ─── Planner ─────────────────────────────────────────────────────────────


class HtnPlanner:
    """Rule-based HTN planner.

    Example
    -------
    >>> planner = HtnPlanner()
    >>> plan = planner.plan(goal, world)
    >>> [s.skill_id for s in plan.steps]
    ['navigate_to', 'reach', 'grasp', 'lift']
    """

    def __init__(self, *, rules: dict[str, Rule] | None = None) -> None:
        self._rules = dict(_RULES) if rules is None else dict(rules)

    def known_predicates(self) -> tuple[str, ...]:
        """Return the predicates this planner knows how to decompose."""
        return tuple(sorted(self._rules.keys()))

    def can_plan(self, goal: Goal) -> bool:
        """Return whether the planner has a rule for this goal."""
        return goal.predicate in self._rules

    def plan(self, goal: Goal, world: WorldState) -> Plan:
        """Return a plan for the given goal and world.

        Raises
        ------
        PlanningError
            If no rule matches the goal's predicate, or if a rule cannot
            decompose the goal (missing object, missing argument, …).
        """
        predicate = goal.predicate
        if predicate is None or predicate not in self._rules:
            raise PlanningError(
                "no rule for goal predicate",
                predicate=predicate,
                goal_id=str(goal.goal_id),
            )
        rule = self._rules[predicate]
        steps = rule(goal, world)
        return Plan(
            plan_id=PlanId(new_id("plan")),
            goal_id=goal.goal_id,
            steps=steps,
            created_at=utc_now(),
        )


__all__ = ["HtnPlanner", "PlanningError", "Rule"]
