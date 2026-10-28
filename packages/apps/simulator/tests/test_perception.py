"""Perception-loop integration: sensor → bus → world model → store.

These tests prove the world in the :class:`~orb_runtime.StateStore` is
updated by perception (not just initialized from the scenario): after
sensor ticks, object poses carry seeded noise and confidences flow from
the sensor.
"""

from __future__ import annotations

from orb_brain import WorldModel
from orb_runtime import EventBus, StateStore
from orb_simulation import MockSensor, table_with_cube
from orb_types import (
    Event,
    EventId,
    EventKind,
    ObjectId,
    Observation,
    new_id,
    utc_now,
)


def _publish(bus: EventBus, obs: Observation) -> None:
    bus.publish(
        Event(
            event_id=EventId(new_id("evt")),
            kind=EventKind.OBSERVATION_CREATED,
            timestamp=utc_now(),
            source="perception",
            payload={"observation": obs},
        )
    )


def _ticked_world(seed: int = 7, confidence: float = 0.9) -> StateStore:
    bus = EventBus()
    store = StateStore(bus, initial_world=table_with_cube("red"))
    model = WorldModel(bus, store)
    model.start()
    sensor = MockSensor(position_noise=0.01, confidence=confidence, seed=seed)
    for obs in sensor.sense(store.world):
        _publish(bus, obs)
    model.stop()
    return store


def test_perception_increments_world_version() -> None:
    store = _ticked_world()
    assert store.world_version == 1


def test_perceived_pose_carries_seeded_noise() -> None:
    store = _ticked_world()
    obj = store.world.get_object(ObjectId("cube_red"))
    assert obj is not None
    # Ground truth is (0, 0, 0.76); noise must have moved it.
    assert (obj.pose.position.x, obj.pose.position.y) != (0.0, 0.0)
    assert abs(obj.pose.position.x) <= 0.01
    assert abs(obj.pose.position.y) <= 0.01


def test_perceived_confidence_flows_from_sensor() -> None:
    store = _ticked_world(confidence=0.9)
    obj = store.world.get_object(ObjectId("cube_red"))
    assert obj is not None
    assert obj.confidence == 0.9


def test_perception_is_deterministic() -> None:
    first = _ticked_world(seed=11).world.get_object(ObjectId("cube_red"))
    second = _ticked_world(seed=11).world.get_object(ObjectId("cube_red"))
    assert first is not None and second is not None
    assert first.pose == second.pose
