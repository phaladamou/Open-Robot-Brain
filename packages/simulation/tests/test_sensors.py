"""Tests for orb_simulation.sensors."""

from __future__ import annotations

import pytest
from orb_simulation import MockSensor, table_with_cube, table_with_cubes
from orb_simulation.environments import empty
from orb_types import ObjectId, ObservationKind


def test_no_noise_reproduces_ground_truth() -> None:
    sensor = MockSensor()
    world = table_with_cube("red")
    (obs,) = sensor.sense(world)
    assert obs.kind is ObservationKind.OBJECT_DETECTED
    assert obs.object_id == ObjectId("cube_red")
    assert obs.pose == world.objects[0].pose
    assert obs.confidence == 1.0
    assert obs.payload["type"] == "cube"
    assert obs.payload["color"] == "red"


def test_one_observation_per_object_in_world_order() -> None:
    sensor = MockSensor(seed=1)
    world = table_with_cubes("red", "blue", "green")
    observations = sensor.sense(world)
    assert [o.object_id for o in observations] == [
        ObjectId("cube_red"),
        ObjectId("cube_blue"),
        ObjectId("cube_green"),
    ]


def test_empty_world_yields_no_observations() -> None:
    sensor = MockSensor(seed=1)
    assert sensor.sense(empty()) == ()


def test_noise_stays_within_bounds() -> None:
    sensor = MockSensor(position_noise=0.01, seed=7)
    world = table_with_cube("red")
    for _ in range(20):
        (obs,) = sensor.sense(world)
        assert obs.pose is not None
        delta = obs.pose.position
        truth = world.objects[0].pose.position
        assert abs(delta.x - truth.x) <= 0.01
        assert abs(delta.y - truth.y) <= 0.01
        assert abs(delta.z - truth.z) <= 0.01


def test_same_seed_produces_identical_stream() -> None:
    world = table_with_cube("red")
    first = MockSensor(position_noise=0.01, seed=42).sense(world)
    second = MockSensor(position_noise=0.01, seed=42).sense(world)
    assert [o.pose for o in first] == [o.pose for o in second]
    assert [o.observation_id for o in first] == [o.observation_id for o in second]


def test_observation_ids_are_unique_across_ticks() -> None:
    sensor = MockSensor(seed=1)
    world = table_with_cube("red")
    first = sensor.sense(world)
    second = sensor.sense(world)
    ids = [o.observation_id for o in (*first, *second)]
    assert len(set(ids)) == 2
    assert sensor.observations_produced == 2


def test_confidence_is_stamped_on_observations() -> None:
    sensor = MockSensor(confidence=0.75)
    (obs,) = sensor.sense(table_with_cube("red"))
    assert obs.confidence == 0.75


def test_source_is_stamped_on_observations() -> None:
    sensor = MockSensor(source="front_rgb")
    (obs,) = sensor.sense(table_with_cube("red"))
    assert obs.source == "front_rgb"


def test_empty_source_rejected() -> None:
    with pytest.raises(ValueError, match="source"):
        MockSensor(source="")


def test_negative_noise_rejected() -> None:
    with pytest.raises(ValueError, match="position_noise"):
        MockSensor(position_noise=-0.1)


def test_confidence_out_of_range_rejected() -> None:
    with pytest.raises(ValueError, match="confidence"):
        MockSensor(confidence=1.5)
    with pytest.raises(ValueError, match="confidence"):
        MockSensor(confidence=-0.1)
