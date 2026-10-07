"""Tests for orb_brain.reasoning.reasoner."""

from __future__ import annotations

import pytest
from orb_brain.reasoning.reasoner import Reasoner
from orb_types import (
    Capability,
    CapabilityId,
    CapabilitySet,
    Goal,
    GoalId,
    GoalKind,
    Object,
    ObjectId,
    WorldState,
    utc_now,
)
from pydantic import ValidationError

# ─── Fakes ───────────────────────────────────────────────────────────────


class FakeCapabilities:
    def __init__(self, *names: str) -> None:
        caps = tuple(Capability(capability_id=CapabilityId(n), name=n) for n in names)
        self._set = CapabilitySet(capabilities=caps)

    def capabilities(self) -> CapabilitySet:
        return self._set


def _world_with(*object_ids: str) -> WorldState:
    return WorldState(
        timestamp=utc_now(),
        objects=tuple(Object(object_id=ObjectId(oid), type="cup") for oid in object_ids),
    )


def _goal(
    *,
    kind: GoalKind = GoalKind.MANIPULATION,
    predicate: str | None = "pick",
    args: dict[str, str] | None = None,
    target_object: ObjectId | None = None,
    description: str = "pick the red cup",
) -> Goal:
    return Goal(
        goal_id=GoalId("goal_01"),
        description=description,
        kind=kind,
        predicate=predicate,
        args=args if args is not None else {"object_type": "cup"},
        target_object=target_object,
        created_at=utc_now(),
    )


# ─── Well-formed ─────────────────────────────────────────────────────────


def test_well_formed_goal_passes() -> None:
    r = Reasoner(FakeCapabilities("can_grasp", "can_lift"))
    result = r.reason(_goal(), _world_with())
    assert result.ok
    assert result.errors == ()


def test_empty_description_rejected_at_construction() -> None:
    with pytest.raises(ValidationError):
        _goal(description="")


def test_no_predicate_and_no_args_fails() -> None:
    r = Reasoner(FakeCapabilities("can_grasp"))
    g = _goal(predicate=None, args={})
    result = r.reason(g, _world_with())
    assert not result.ok


# ─── Reachable ───────────────────────────────────────────────────────────


def test_missing_target_object_fails() -> None:
    r = Reasoner(FakeCapabilities("can_grasp", "can_lift"))
    g = _goal(target_object=ObjectId("cup_01"))
    result = r.reason(g, _world_with())  # world is empty
    assert not result.ok
    assert any("not found" in e for e in result.errors)


def test_present_target_object_passes() -> None:
    r = Reasoner(FakeCapabilities("can_grasp", "can_lift"))
    g = _goal(target_object=ObjectId("cup_01"))
    result = r.reason(g, _world_with("cup_01"))
    assert result.ok


def test_missing_location_warns_but_passes() -> None:
    r = Reasoner(FakeCapabilities("can_navigate"))
    g = _goal(
        kind=GoalKind.NAVIGATION,
        predicate="at",
        args={"location": "kitchen"},
        target_object=None,
    )
    result = r.reason(g, _world_with())
    assert result.ok
    assert any("kitchen" in w for w in result.warnings)


# ─── Feasible ────────────────────────────────────────────────────────────


def test_pick_requires_grasp_and_lift() -> None:
    r = Reasoner(FakeCapabilities("can_grasp"))  # missing can_lift
    result = r.reason(_goal(predicate="pick"), _world_with())
    assert not result.ok
    assert any("can_lift" in e for e in result.errors)


def test_pick_succeeds_with_both_capabilities() -> None:
    r = Reasoner(FakeCapabilities("can_grasp", "can_lift"))
    result = r.reason(_goal(predicate="pick"), _world_with())
    assert result.ok


def test_navigation_requires_navigate() -> None:
    r = Reasoner(FakeCapabilities("can_grasp"))  # wrong capability
    g = _goal(
        kind=GoalKind.NAVIGATION,
        predicate="at",
        args={"location": "kitchen"},
    )
    result = r.reason(g, _world_with())
    assert not result.ok
    assert any("can_navigate" in e for e in result.errors)


def test_perceptual_requires_see() -> None:
    r = Reasoner(FakeCapabilities())
    g = _goal(kind=GoalKind.PERCEPTUAL, predicate="known", args={"object_type": "cup"})
    result = r.reason(g, _world_with())
    assert not result.ok
    assert any("can_see" in e for e in result.errors)


def test_unknown_kind_predicate_has_no_requirement() -> None:
    r = Reasoner(FakeCapabilities())
    g = _goal(kind=GoalKind.OTHER, predicate="weird", args={"x": "y"})
    result = r.reason(g, _world_with())
    assert result.ok


# ─── Multiple errors accumulate ──────────────────────────────────────────


def test_multiple_errors_accumulate() -> None:
    r = Reasoner(FakeCapabilities())  # no capabilities
    g = _goal(
        predicate="pick",
        target_object=ObjectId("missing_object"),
    )
    result = r.reason(g, _world_with())
    assert not result.ok
    assert len(result.errors) >= 2


# ─── Determinism ─────────────────────────────────────────────────────────


def test_reasoning_is_deterministic() -> None:
    r = Reasoner(FakeCapabilities("can_grasp"))
    g = _goal(predicate="pick")
    world = _world_with()
    a = r.reason(g, world)
    b = r.reason(g, world)
    assert a.errors == b.errors
    assert a.ok == b.ok
