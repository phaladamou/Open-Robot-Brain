"""Tests for orb_types.observation."""

from __future__ import annotations

import pytest
from orb_types.base import utc_now
from orb_types.geometry import Pose, Vec3
from orb_types.ids import ObjectId, ObservationId
from orb_types.observation import (
    Observation,
    ObservationKind,
    SensorModality,
    SensorReading,
)
from pydantic import ValidationError as PydanticValidationError

# ─── SensorReading ───────────────────────────────────────────────────────


def test_sensor_reading_minimal() -> None:
    r = SensorReading(
        modality=SensorModality.VISION,
        source="front_rgb",
        timestamp=utc_now(),
    )
    assert r.modality == SensorModality.VISION
    assert r.confidence == 1.0
    assert r.payload == {}


def test_sensor_reading_with_payload() -> None:
    r = SensorReading(
        modality=SensorModality.DEPTH,
        source="front_depth",
        timestamp=utc_now(),
        confidence=0.9,
        payload={"min_depth": 0.1, "max_depth": 5.0},
    )
    assert r.payload["min_depth"] == 0.1
    assert r.confidence == 0.9


def test_sensor_reading_rejects_bad_confidence() -> None:
    with pytest.raises(PydanticValidationError):
        SensorReading(
            modality=SensorModality.VISION,
            source="x",
            timestamp=utc_now(),
            confidence=1.5,
        )


# ─── Observation ─────────────────────────────────────────────────────────


def test_observation_minimal() -> None:
    o = Observation(
        observation_id=ObservationId("obs_01"),
        kind=ObservationKind.SCENE,
        timestamp=utc_now(),
    )
    assert o.kind == ObservationKind.SCENE
    assert o.source == "perception"
    assert o.confidence == 1.0
    assert o.payload == {}
    assert o.readings == ()


def test_observation_object_detected() -> None:
    o = Observation(
        observation_id=ObservationId("obs_02"),
        kind=ObservationKind.OBJECT_DETECTED,
        timestamp=utc_now(),
        source="perception",
        object_id=ObjectId("cup_01"),
        pose=Pose(position=Vec3(x=1.0, y=0.5, z=0.8)),
        confidence=0.94,
        payload={"type": "cup", "color": "red"},
    )
    assert o.object_id == "cup_01"
    assert o.pose is not None
    assert o.pose.position.x == 1.0
    assert o.confidence == 0.94
    assert o.payload["color"] == "red"


def test_observation_with_readings() -> None:
    r = SensorReading(
        modality=SensorModality.VISION,
        source="front_rgb",
        timestamp=utc_now(),
    )
    o = Observation(
        observation_id=ObservationId("obs_03"),
        kind=ObservationKind.SCENE,
        timestamp=utc_now(),
        readings=(r,),
    )
    assert len(o.readings) == 1


def test_observation_frozen() -> None:
    o = Observation(
        observation_id=ObservationId("obs_04"),
        kind=ObservationKind.SCENE,
        timestamp=utc_now(),
    )
    with pytest.raises(PydanticValidationError):
        o.confidence = 0.5  # type: ignore[misc]


def test_observation_kind_is_serializable() -> None:
    o = Observation(
        observation_id=ObservationId("obs_05"),
        kind=ObservationKind.OBJECT_DETECTED,
        timestamp=utc_now(),
    )
    d = o.to_dict()
    assert d["kind"] == "object_detected"
