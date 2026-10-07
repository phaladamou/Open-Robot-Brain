"""Tests for orb_brain.world_model.model."""

from __future__ import annotations

import pytest
from orb_brain.world_model import WorldModel
from orb_runtime import EventBus, StateStore
from orb_types import (
    Event,
    EventId,
    EventKind,
    ObjectId,
    Observation,
    ObservationId,
    ObservationKind,
    Pose,
    Vec3,
    WorldState,
    utc_now,
)

# ─── Fixtures ────────────────────────────────────────────────────────────


@pytest.fixture
def bus() -> EventBus:
    return EventBus()


@pytest.fixture
def store(bus: EventBus) -> StateStore:
    return StateStore(bus, initial_world=WorldState(timestamp=utc_now()))


def _object_detected(
    object_id: str = "cup_01",
    *,
    pose: Pose | None = None,
    confidence: float = 1.0,
    payload: dict[str, object] | None = None,
) -> Observation:
    return Observation(
        observation_id=ObservationId(f"obs_{object_id}"),
        kind=ObservationKind.OBJECT_DETECTED,
        timestamp=utc_now(),
        object_id=ObjectId(object_id),
        pose=pose,
        confidence=confidence,
        payload=payload or {"type": "cup"},
    )


# ─── Lifecycle ───────────────────────────────────────────────────────────


def test_model_starts_stopped(bus: EventBus, store: StateStore) -> None:
    m = WorldModel(bus, store)
    assert not m.running


def test_model_start_subscribes(bus: EventBus, store: StateStore) -> None:
    m = WorldModel(bus, store)
    m.start()
    assert m.running
    assert bus.subscriber_count(kind=EventKind.OBSERVATION_CREATED) == 1


def test_model_start_is_idempotent(bus: EventBus, store: StateStore) -> None:
    m = WorldModel(bus, store)
    m.start()
    m.start()
    assert bus.subscriber_count(kind=EventKind.OBSERVATION_CREATED) == 1


def test_model_stop_unsubscribes(bus: EventBus, store: StateStore) -> None:
    m = WorldModel(bus, store)
    m.start()
    m.stop()
    assert not m.running
    assert bus.subscriber_count(kind=EventKind.OBSERVATION_CREATED) == 0


# ─── apply_observation directly ──────────────────────────────────────────


def test_object_detected_adds_object(bus: EventBus, store: StateStore) -> None:
    m = WorldModel(bus, store)
    obs = _object_detected("cup_01", pose=Pose(position=Vec3(x=1.0)))
    m.apply_observation(obs)

    obj = store.world.get_object(ObjectId("cup_01"))
    assert obj is not None
    assert obj.type == "cup"
    assert obj.pose.position.x == 1.0


def test_object_detected_replaces_existing(bus: EventBus, store: StateStore) -> None:
    m = WorldModel(bus, store)
    m.apply_observation(_object_detected("cup_01", pose=Pose(position=Vec3(x=1.0))))
    m.apply_observation(_object_detected("cup_01", pose=Pose(position=Vec3(x=2.0))))

    assert len(store.world.objects) == 1
    obj = store.world.get_object(ObjectId("cup_01"))
    assert obj is not None
    assert obj.pose.position.x == 2.0


def test_object_lost_removes_object(bus: EventBus, store: StateStore) -> None:
    m = WorldModel(bus, store)
    m.apply_observation(_object_detected("cup_01"))
    assert store.world.get_object(ObjectId("cup_01")) is not None

    lost = Observation(
        observation_id=ObservationId("obs_lost"),
        kind=ObservationKind.OBJECT_LOST,
        timestamp=utc_now(),
        object_id=ObjectId("cup_01"),
    )
    m.apply_observation(lost)
    assert store.world.get_object(ObjectId("cup_01")) is None


def test_object_lost_on_unknown_is_noop(bus: EventBus, store: StateStore) -> None:
    m = WorldModel(bus, store)
    version_before = store.world_version
    lost = Observation(
        observation_id=ObservationId("obs_lost"),
        kind=ObservationKind.OBJECT_LOST,
        timestamp=utc_now(),
        object_id=ObjectId("does_not_exist"),
    )
    m.apply_observation(lost)
    assert store.world_version == version_before


def test_scene_is_noop(bus: EventBus, store: StateStore) -> None:
    m = WorldModel(bus, store)
    before = store.world_version
    scene = Observation(
        observation_id=ObservationId("obs_scene"),
        kind=ObservationKind.SCENE,
        timestamp=utc_now(),
    )
    m.apply_observation(scene)
    assert store.world_version == before


def test_unsupported_kind_is_ignored(bus: EventBus, store: StateStore) -> None:
    m = WorldModel(bus, store)
    before = store.world_version
    obs = Observation(
        observation_id=ObservationId("obs_speech"),
        kind=ObservationKind.SPEECH,
        timestamp=utc_now(),
    )
    m.apply_observation(obs)
    assert store.world_version == before


def test_object_detected_without_object_id_is_ignored(bus: EventBus, store: StateStore) -> None:
    m = WorldModel(bus, store)
    before = store.world_version
    obs = Observation(
        observation_id=ObservationId("obs_noid"),
        kind=ObservationKind.OBJECT_DETECTED,
        timestamp=utc_now(),
        object_id=None,
    )
    m.apply_observation(obs)
    assert store.world_version == before


# ─── Confidence threshold ────────────────────────────────────────────────


def test_low_confidence_dropped(bus: EventBus, store: StateStore) -> None:
    m = WorldModel(bus, store, confidence_threshold=0.5)
    m.apply_observation(_object_detected("cup_01", confidence=0.3))
    assert store.world.get_object(ObjectId("cup_01")) is None


def test_high_confidence_accepted(bus: EventBus, store: StateStore) -> None:
    m = WorldModel(bus, store, confidence_threshold=0.5)
    m.apply_observation(_object_detected("cup_01", confidence=0.8))
    assert store.world.get_object(ObjectId("cup_01")) is not None


def test_threshold_property(bus: EventBus, store: StateStore) -> None:
    m = WorldModel(bus, store, confidence_threshold=0.7)
    assert m.confidence_threshold == 0.7


# ─── Bus integration ─────────────────────────────────────────────────────


def test_start_then_bus_delivers_observation(bus: EventBus, store: StateStore) -> None:
    m = WorldModel(bus, store)
    m.start()

    obs = _object_detected("cup_01", payload={"type": "cup", "color": "red"})
    event = Event(
        event_id=EventId("evt_obs"),
        kind=EventKind.OBSERVATION_CREATED,
        timestamp=utc_now(),
        payload={"observation": obs},
    )
    bus.publish(event)

    obj = store.world.get_object(ObjectId("cup_01"))
    assert obj is not None
    assert obj.attributes.get("color") == "red"


def test_bus_event_without_observation_is_ignored(bus: EventBus, store: StateStore) -> None:
    m = WorldModel(bus, store)
    m.start()
    before = store.world_version

    event = Event(
        event_id=EventId("evt_untyped"),
        kind=EventKind.OBSERVATION_CREATED,
        timestamp=utc_now(),
        payload={},  # no "observation" key
    )
    bus.publish(event)
    assert store.world_version == before


def test_stop_prevents_further_updates(bus: EventBus, store: StateStore) -> None:
    m = WorldModel(bus, store)
    m.start()
    m.stop()

    obs = _object_detected("cup_01")
    event = Event(
        event_id=EventId("evt_obs"),
        kind=EventKind.OBSERVATION_CREATED,
        timestamp=utc_now(),
        payload={"observation": obs},
    )
    bus.publish(event)
    assert store.world.get_object(ObjectId("cup_01")) is None
