"""Tests for orb_brain.planning.htn."""

from __future__ import annotations

import pytest
from orb_brain.planning import HtnPlanner
from orb_types import (
    Goal,
    GoalId,
    GoalKind,
    Object,
    ObjectId,
    PlanningError,
    WorldState,
    utc_now,
)

# ─── Fixtures ────────────────────────────────────────────────────────────


@pytest.fixture
def planner() -> HtnPlanner:
    return HtnPlanner()


@pytest.fixture
def world() -> WorldState:
    return WorldState(
        timestamp=utc_now(),
        objects=(
            Object(
                object_id=ObjectId("cup_01"),
                type="cup",
                attributes={"color": "red"},
            ),
            Object(
                object_id=ObjectId("cup_02"),
                type="cup",
                attributes={"color": "blue"},
            ),
            Object(
                object_id=ObjectId("drawer_01"),
                type="drawer",
            ),
        ),
    )


def _goal(
    *,
    predicate: str | None = "pick",
    kind: GoalKind = GoalKind.MANIPULATION,
    args: dict[str, str] | None = None,
    target_object: ObjectId | None = None,
    target_location: str | None = None,
    description: str = "pick the red cup",
) -> Goal:
    return Goal(
        goal_id=GoalId("goal_01"),
        description=description,
        kind=kind,
        predicate=predicate,
        args=args if args is not None else {"object_type": "cup", "color": "red"},
        target_object=target_object,
        target_location=target_location,
        created_at=utc_now(),
    )


# ─── Predicates ──────────────────────────────────────────────────────────


def test_known_predicates(planner: HtnPlanner) -> None:
    preds = planner.known_predicates()
    assert "pick" in preds
    assert "place" in preds
    assert "at" in preds
    assert "open" in preds
    assert "close" in preds
    assert "known" in preds


def test_can_plan_true(planner: HtnPlanner) -> None:
    assert planner.can_plan(_goal(predicate="pick"))


def test_can_plan_false(planner: HtnPlanner) -> None:
    assert not planner.can_plan(_goal(predicate="teleport"))


# ─── Pick ────────────────────────────────────────────────────────────────


def test_pick_decomposes_into_four_steps(planner: HtnPlanner, world: WorldState) -> None:
    plan = planner.plan(_goal(predicate="pick", args={"object_type": "cup", "color": "red"}), world)
    assert len(plan.steps) == 4
    assert [s.skill_id for s in plan.steps] == ["navigate_to", "reach", "grasp", "lift"]


def test_pick_resolves_red_cup(planner: HtnPlanner, world: WorldState) -> None:
    plan = planner.plan(_goal(predicate="pick", args={"object_type": "cup", "color": "red"}), world)
    assert plan.steps[0].parameters["object_id"] == "cup_01"


def test_pick_resolves_blue_cup(planner: HtnPlanner, world: WorldState) -> None:
    goal = _goal(predicate="pick", args={"object_type": "cup", "color": "blue"})
    plan = planner.plan(goal, world)
    assert plan.steps[0].parameters["object_id"] == "cup_02"


def test_pick_with_explicit_object_id(planner: HtnPlanner, world: WorldState) -> None:
    goal = _goal(predicate="pick", args={}, target_object=ObjectId("cup_01"))
    plan = planner.plan(goal, world)
    assert plan.steps[0].parameters["object_id"] == "cup_01"


def test_pick_with_explicit_missing_object_raises(planner: HtnPlanner, world: WorldState) -> None:
    goal = _goal(predicate="pick", args={}, target_object=ObjectId("cup_99"))
    with pytest.raises(PlanningError, match="not present"):
        planner.plan(goal, world)


def test_pick_no_match_raises(planner: HtnPlanner, world: WorldState) -> None:
    goal = _goal(predicate="pick", args={"object_type": "cup", "color": "green"})
    with pytest.raises(PlanningError, match="no matching"):
        planner.plan(goal, world)


def test_pick_no_type_no_id_raises(planner: HtnPlanner, world: WorldState) -> None:
    goal = _goal(predicate="pick", args={})
    with pytest.raises(PlanningError):
        planner.plan(goal, world)


# ─── Place ───────────────────────────────────────────────────────────────


def test_place_decomposes(planner: HtnPlanner, world: WorldState) -> None:
    goal = _goal(
        predicate="place",
        args={"object_type": "cup", "color": "red", "target": "table"},
    )
    plan = planner.plan(goal, world)
    assert [s.skill_id for s in plan.steps] == ["navigate_to", "reach", "release"]
    assert plan.steps[0].parameters["location"] == "table"


def test_place_missing_target_raises(planner: HtnPlanner, world: WorldState) -> None:
    goal = _goal(predicate="place", args={"object_type": "cup", "color": "red"})
    with pytest.raises(PlanningError, match="target"):
        planner.plan(goal, world)


# ─── Navigation ──────────────────────────────────────────────────────────


def test_navigate_decomposes(planner: HtnPlanner, world: WorldState) -> None:
    goal = _goal(
        predicate="at",
        kind=GoalKind.NAVIGATION,
        args={"location": "kitchen"},
        target_location="kitchen",
    )
    plan = planner.plan(goal, world)
    assert len(plan.steps) == 1
    assert plan.steps[0].skill_id == "navigate_to"
    assert plan.steps[0].parameters["location"] == "kitchen"


def test_navigate_from_target_location_only(planner: HtnPlanner, world: WorldState) -> None:
    goal = _goal(
        predicate="at",
        kind=GoalKind.NAVIGATION,
        args={},
        target_location="kitchen",
    )
    plan = planner.plan(goal, world)
    assert plan.steps[0].parameters["location"] == "kitchen"


def test_navigate_missing_location_raises(planner: HtnPlanner, world: WorldState) -> None:
    goal = _goal(predicate="at", kind=GoalKind.NAVIGATION, args={})
    with pytest.raises(PlanningError, match="location"):
        planner.plan(goal, world)


# ─── Open / close ────────────────────────────────────────────────────────


def test_open_decomposes(planner: HtnPlanner, world: WorldState) -> None:
    goal = _goal(
        predicate="open",
        args={"object_type": "drawer"},
        target_object=ObjectId("drawer_01"),
        description="open the drawer",
    )
    plan = planner.plan(goal, world)
    assert [s.skill_id for s in plan.steps] == ["navigate_to", "reach", "pull"]


def test_close_decomposes(planner: HtnPlanner, world: WorldState) -> None:
    goal = _goal(
        predicate="close",
        args={"object_type": "drawer"},
        target_object=ObjectId("drawer_01"),
        description="close the drawer",
    )
    plan = planner.plan(goal, world)
    assert [s.skill_id for s in plan.steps] == ["navigate_to", "reach", "push"]


# ─── Perceptual ──────────────────────────────────────────────────────────


def test_find_decomposes(planner: HtnPlanner, world: WorldState) -> None:
    goal = _goal(
        predicate="known",
        kind=GoalKind.PERCEPTUAL,
        args={"object_type": "cup"},
    )
    plan = planner.plan(goal, world)
    assert len(plan.steps) == 1
    assert plan.steps[0].skill_id == "inspect"


# ─── Errors ──────────────────────────────────────────────────────────────


def test_unknown_predicate_raises(planner: HtnPlanner, world: WorldState) -> None:
    goal = _goal(predicate="teleport", args={})
    with pytest.raises(PlanningError, match="no rule"):
        planner.plan(goal, world)


def test_none_predicate_raises(planner: HtnPlanner, world: WorldState) -> None:
    goal = _goal(predicate=None, args={})
    with pytest.raises(PlanningError):
        planner.plan(goal, world)


# ─── Custom rules ────────────────────────────────────────────────────────


def test_custom_rules_replace_defaults(world: WorldState) -> None:
    from orb_types import PlanStep, SkillId

    def custom(goal: Goal, w: WorldState) -> tuple[PlanStep, ...]:
        return (PlanStep(step_id="only", skill_id=SkillId("noop")),)

    planner = HtnPlanner(rules={"pick": custom})
    plan = planner.plan(_goal(predicate="pick", args={"object_type": "cup"}), world)
    assert len(plan.steps) == 1
    assert plan.steps[0].skill_id == "noop"


# ─── Plan invariants ─────────────────────────────────────────────────────


def test_plan_has_unique_id(planner: HtnPlanner, world: WorldState) -> None:
    p1 = planner.plan(_goal(predicate="pick", args={"object_type": "cup", "color": "red"}), world)
    p2 = planner.plan(_goal(predicate="pick", args={"object_type": "cup", "color": "red"}), world)
    assert p1.plan_id != p2.plan_id


def test_plan_steps_are_indexed(planner: HtnPlanner, world: WorldState) -> None:
    plan = planner.plan(_goal(predicate="pick", args={"object_type": "cup", "color": "red"}), world)
    assert [s.step_id for s in plan.steps] == ["step_1", "step_2", "step_3", "step_4"]
