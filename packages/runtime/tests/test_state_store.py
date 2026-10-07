"""Tests for orb_runtime.state.store."""

from __future__ import annotations

from orb_runtime.events.bus import EventBus
from orb_runtime.state.store import StateStore
from orb_types import (
    Event,
    EventId,
    EventKind,
    Object,
    ObjectId,
    RobotId,
    RobotState,
    WorldState,
    utc_now,
)


def _world(version: int = 0, *, n_objects: int = 0) -> WorldState:
    objects = tuple(Object(object_id=ObjectId(f"obj_{i}"), type="cube") for i in range(n_objects))
    return WorldState(timestamp=utc_now(), version=version, objects=objects)


def _robot() -> RobotState:
    return RobotState(robot_id=RobotId("r2d2"), timestamp=utc_now())


# ─── Constructor ─────────────────────────────────────────────────────────


def test_init_requires_world() -> None:
    bus = EventBus()
    world = _world(version=3)
    store = StateStore(bus, initial_world=world)
    assert store.world is world
    assert store.robot is None
    assert store.world_version == 3
    assert store.robot_version == 0


# ─── update_world ────────────────────────────────────────────────────────


def test_update_world_replaces_and_increments_version() -> None:
    bus = EventBus()
    store = StateStore(bus, initial_world=_world(version=0))
    new_world = _world(version=0, n_objects=2)
    store.update_world(new_world)

    assert store.world_version == 1
    assert len(store.world.objects) == 2
    # The store overrides the version to keep monotonicity
    assert store.world.version == 1


def test_update_world_publishes_event() -> None:
    bus = EventBus()
    received: list[Event] = []
    bus.subscribe(received.append, kind=EventKind.WORLD_UPDATED)

    store = StateStore(bus, initial_world=_world())
    store.update_world(_world())

    assert len(received) == 1
    e = received[0]
    assert e.source == "state_store"
    assert e.payload["version"] == 1


def test_update_world_propagates_correlation_id() -> None:
    bus = EventBus()
    received: list[Event] = []
    bus.subscribe(received.append, kind=EventKind.WORLD_UPDATED)

    store = StateStore(bus, initial_world=_world())
    store.update_world(_world(), correlation_id="task_abc")

    assert received[0].correlation_id == "task_abc"


def test_update_world_ignores_caller_version() -> None:
    bus = EventBus()
    store = StateStore(bus, initial_world=_world(version=10))
    # Caller passes a bogus version
    store.update_world(_world(version=999))
    assert store.world_version == 11
    assert store.world.version == 11


def test_multiple_updates_monotonic() -> None:
    bus = EventBus()
    store = StateStore(bus, initial_world=_world())
    for _ in range(5):
        store.update_world(_world())
    assert store.world_version == 5


# ─── update_robot ────────────────────────────────────────────────────────


def test_update_robot_sets_and_increments() -> None:
    bus = EventBus()
    store = StateStore(bus, initial_world=_world())
    store.update_robot(_robot())
    assert store.robot is not None
    assert store.robot.robot_id == "r2d2"
    assert store.robot_version == 1


def test_update_robot_publishes_custom_event() -> None:
    bus = EventBus()
    received: list[Event] = []
    bus.subscribe(received.append, kind=EventKind.CUSTOM)

    store = StateStore(bus, initial_world=_world())
    store.update_robot(_robot())

    assert len(received) == 1
    e = received[0]
    assert e.source == "state_store"
    assert e.payload["kind_label"] == "robot.updated"
    assert e.payload["version"] == 1
    assert e.payload["robot_id"] == "r2d2"


def test_update_robot_correlation() -> None:
    bus = EventBus()
    received: list[Event] = []
    bus.subscribe(received.append, kind=EventKind.CUSTOM)

    store = StateStore(bus, initial_world=_world())
    store.update_robot(_robot(), correlation_id="session_01")

    assert received[0].correlation_id == "session_01"


# ─── reset ───────────────────────────────────────────────────────────────


def test_reset_clears_robot() -> None:
    bus = EventBus()
    store = StateStore(bus, initial_world=_world())
    store.update_robot(_robot())
    store.reset()

    robot_after = store.robot
    version_after = store.robot_version
    assert robot_after is None
    assert version_after == 0


def test_reset_with_new_world() -> None:
    bus = EventBus()
    store = StateStore(bus, initial_world=_world(version=5))
    store.reset(world=_world(version=42))
    assert store.world.version == 42
    assert store.world_version == 42


def test_update_after_reset_increments() -> None:
    bus = EventBus()
    store = StateStore(bus, initial_world=_world(version=5))
    store.reset(world=_world(version=42))
    before = store.world_version
    store.update_world(_world())
    after = store.world_version
    assert after == before + 1
    assert after == 43


def test_update_after_reset_increments_from_new_base() -> None:
    bus = EventBus()
    store = StateStore(bus, initial_world=_world(version=5))
    store.reset(world=_world(version=42))
    store.update_world(_world())
    assert store.world_version == 43


# ─── Isolation ───────────────────────────────────────────────────────────


def test_store_does_not_couple_world_and_robot_versions() -> None:
    bus = EventBus()
    store = StateStore(bus, initial_world=_world())
    store.update_world(_world())
    store.update_world(_world())
    store.update_robot(_robot())
    assert store.world_version == 2
    assert store.robot_version == 1


def test_unrelated_events_do_not_affect_store() -> None:
    bus = EventBus()
    store = StateStore(bus, initial_world=_world())

    # Publish an unrelated event
    bus.publish(
        Event(
            event_id=EventId("evt_unrelated"),
            kind=EventKind.RUNTIME_STARTED,
            timestamp=utc_now(),
        )
    )

    world_v = store.world_version
    robot_after = store.robot
    assert world_v == 0
    assert robot_after is None
