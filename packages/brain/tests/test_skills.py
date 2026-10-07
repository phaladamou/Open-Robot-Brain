"""Tests for orb_brain.skills (base, builtin, registry)."""

from __future__ import annotations

from typing import Any

import pytest
from orb_brain.skills import (
    BaseSkill,
    GraspSkill,
    InMemorySkillRegistry,
    InspectSkill,
    LiftSkill,
    NavigateToSkill,
    PullSkill,
    PushSkill,
    ReachSkill,
    ReleaseSkill,
)
from orb_runtime import EventBus
from orb_types import (
    Event,
    EventKind,
    Location,
    Object,
    ObjectId,
    SkillId,
    SkillResult,
    SkillStatus,
    WorldState,
    utc_now,
)

# ─── Fixtures ────────────────────────────────────────────────────────────


@pytest.fixture
def bus() -> EventBus:
    return EventBus()


@pytest.fixture
def world() -> WorldState:
    return WorldState(
        timestamp=utc_now(),
        objects=(
            Object(object_id=ObjectId("cup_01"), type="cup", attributes={"color": "red"}),
            Object(object_id=ObjectId("drawer_01"), type="drawer"),
        ),
        locations=(Location(name="kitchen"),),
    )


@pytest.fixture
def registry(bus: EventBus) -> InMemorySkillRegistry:
    r = InMemorySkillRegistry(bus)
    r.register_many(
        NavigateToSkill(),
        ReachSkill(),
        GraspSkill(),
        LiftSkill(),
        ReleaseSkill(),
        PullSkill(),
        PushSkill(),
        InspectSkill(),
    )
    return r


# ─── BaseSkill ───────────────────────────────────────────────────────────


def test_base_skill_is_abstract() -> None:
    with pytest.raises(TypeError):
        BaseSkill()  # type: ignore[abstract]


def test_spec_exposes_declarative_description() -> None:
    skill = GraspSkill()
    assert skill.spec.skill_id == "grasp"
    assert skill.spec.name == "grasp"


# ─── Builtin skills — direct calls ───────────────────────────────────────


def test_navigate_to_object(world: WorldState) -> None:
    r = NavigateToSkill().run({"object_id": "cup_01"}, world)
    assert r.status is SkillStatus.SUCCEEDED


def test_navigate_to_missing_object_fails(world: WorldState) -> None:
    r = NavigateToSkill().run({"object_id": "cup_99"}, world)
    assert r.status is SkillStatus.FAILED
    assert "not in world" in (r.message or "")


def test_navigate_to_location(world: WorldState) -> None:
    r = NavigateToSkill().run({"location": "kitchen"}, world)
    assert r.status is SkillStatus.SUCCEEDED


def test_navigate_to_unknown_location_soft_succeeds(world: WorldState) -> None:
    r = NavigateToSkill().run({"location": "unknown"}, world)
    assert r.status is SkillStatus.SUCCEEDED


def test_navigate_to_no_args_fails(world: WorldState) -> None:
    r = NavigateToSkill().run({}, world)
    assert r.status is SkillStatus.FAILED


def test_reach_ok(world: WorldState) -> None:
    r = ReachSkill().run({"object_id": "cup_01"}, world)
    assert r.status is SkillStatus.SUCCEEDED


def test_reach_missing_object(world: WorldState) -> None:
    r = ReachSkill().run({"object_id": "cup_99"}, world)
    assert r.status is SkillStatus.FAILED


def test_reach_missing_param(world: WorldState) -> None:
    r = ReachSkill().run({}, world)
    assert r.status is SkillStatus.FAILED


def test_grasp_ok(world: WorldState) -> None:
    r = GraspSkill().run({"object_id": "cup_01"}, world)
    assert r.status is SkillStatus.SUCCEEDED
    assert r.payload["held"] is True


def test_grasp_missing_object(world: WorldState) -> None:
    r = GraspSkill().run({"object_id": "cup_99"}, world)
    assert r.status is SkillStatus.FAILED


def test_lift_ok(world: WorldState) -> None:
    r = LiftSkill().run({"object_id": "cup_01"}, world)
    assert r.status is SkillStatus.SUCCEEDED
    assert r.payload["lifted"] is True


def test_release_always_succeeds(world: WorldState) -> None:
    r = ReleaseSkill().run({"object_id": "cup_01"}, world)
    assert r.status is SkillStatus.SUCCEEDED
    # Release does not require the object to be present.
    r2 = ReleaseSkill().run({"object_id": "nonexistent"}, world)
    assert r2.status is SkillStatus.SUCCEEDED


def test_release_requires_param(world: WorldState) -> None:
    r = ReleaseSkill().run({}, world)
    assert r.status is SkillStatus.FAILED


def test_pull_ok(world: WorldState) -> None:
    r = PullSkill().run({"object_id": "drawer_01"}, world)
    assert r.status is SkillStatus.SUCCEEDED


def test_pull_missing_object(world: WorldState) -> None:
    r = PullSkill().run({"object_id": "drawer_99"}, world)
    assert r.status is SkillStatus.FAILED


def test_push_ok(world: WorldState) -> None:
    r = PushSkill().run({"object_id": "drawer_01"}, world)
    assert r.status is SkillStatus.SUCCEEDED


def test_inspect_always_succeeds(world: WorldState) -> None:
    r = InspectSkill().run({"target": "cup"}, world)
    assert r.status is SkillStatus.SUCCEEDED


# ─── Registry ────────────────────────────────────────────────────────────


def test_registry_has_skill(registry: InMemorySkillRegistry) -> None:
    assert registry.has(SkillId("grasp"))
    assert not registry.has(SkillId("teleport"))


def test_registry_get_returns_skill_spec(registry: InMemorySkillRegistry) -> None:
    spec = registry.get(SkillId("grasp"))
    assert spec is not None
    assert spec.skill_id == "grasp"


def test_registry_get_unknown_returns_none(registry: InMemorySkillRegistry) -> None:
    assert registry.get(SkillId("teleport")) is None


def test_registry_skill_ids(registry: InMemorySkillRegistry) -> None:
    ids = registry.skill_ids()
    assert "grasp" in ids
    assert "navigate_to" in ids
    assert len(ids) == 8


def test_registry_execute_dispatches_to_skill(
    registry: InMemorySkillRegistry, world: WorldState
) -> None:
    r = registry.execute(SkillId("grasp"), {"object_id": "cup_01"}, world)
    assert r.status is SkillStatus.SUCCEEDED


def test_registry_execute_unknown_raises(
    registry: InMemorySkillRegistry, world: WorldState
) -> None:
    with pytest.raises(KeyError, match="teleport"):
        registry.execute(SkillId("teleport"), {}, world)


def test_registry_publishes_started_and_finished(
    registry: InMemorySkillRegistry, world: WorldState, bus: EventBus
) -> None:
    events: list[Event] = []
    bus.subscribe(events.append)

    registry.execute(SkillId("grasp"), {"object_id": "cup_01"}, world)

    kinds = [e.kind for e in events]
    assert EventKind.SKILL_STARTED in kinds
    assert EventKind.SKILL_FINISHED in kinds


def test_registry_skill_finished_has_status(
    registry: InMemorySkillRegistry, world: WorldState, bus: EventBus
) -> None:
    events: list[Event] = []
    bus.subscribe(events.append, kind=EventKind.SKILL_FINISHED)

    registry.execute(SkillId("grasp"), {"object_id": "cup_01"}, world)

    assert len(events) == 1
    assert events[0].payload["status"] == "succeeded"
    assert events[0].payload["skill_id"] == "grasp"


def test_registry_skill_finished_warning_on_failure(
    registry: InMemorySkillRegistry, world: WorldState, bus: EventBus
) -> None:
    events: list[Event] = []
    bus.subscribe(events.append, kind=EventKind.SKILL_FINISHED)

    registry.execute(SkillId("grasp"), {"object_id": "cup_99"}, world)

    assert events[0].payload["status"] == "failed"


def test_registry_re_register_overwrites(bus: EventBus, world: WorldState) -> None:
    class CustomGrasp(GraspSkill):
        def run(self, parameters: dict[str, Any], world: WorldState) -> SkillResult:
            return self._success(message="custom")

    r = InMemorySkillRegistry(bus)
    r.register(GraspSkill())
    r.register(CustomGrasp())

    result = r.execute(SkillId("grasp"), {"object_id": "cup_01"}, world)
    assert result.message == "custom"
