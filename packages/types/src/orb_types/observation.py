"""Observation types for Open Robot Brain.

An **observation** is a structured snapshot of what a sensor perceived at a
given time. Observations feed the world model; they never control the robot.

Design
------
- Hybrid model: a typed ``kind`` (enum) + optional modality-specific fields +
  an extensible ``payload`` for anything not yet modeled.
- Every observation carries a ``confidence`` in ``[0, 1]``.
- Observations are **immutable** and **timestamped**.
- Sensor-level readings (one per modality) are represented by
  :class:`SensorReading`; a fused / high-level observation is represented by
  :class:`Observation`.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Any

from pydantic import Field

from orb_types.base import ORBModel, Timestamp
from orb_types.geometry import Pose, Vec3
from orb_types.ids import AgentId, ObjectId, ObservationId, RobotId

# ─── Enums ───────────────────────────────────────────────────────────────


class SensorModality(StrEnum):
    """Physical modality of a sensor."""

    VISION = "vision"
    DEPTH = "depth"
    AUDIO = "audio"
    TACTILE = "tactile"
    FORCE = "force"
    IMU = "imu"
    JOINT_ENCODER = "joint_encoder"
    LIDAR = "lidar"
    OTHER = "other"


class ObservationKind(StrEnum):
    """Semantic kind of a fused observation.

    ``kind`` describes *what the brain is being told*, not *how it was sensed*.
    """

    # Perception of the world
    OBJECT_DETECTED = "object_detected"
    OBJECT_LOST = "object_lost"
    SCENE = "scene"
    # Perception of the body
    ROBOT_POSE = "robot_pose"
    JOINT_STATE = "joint_state"
    # Perception of agents
    AGENT_DETECTED = "agent_detected"
    # Interaction
    CONTACT = "contact"
    COLLISION = "collision"
    # Language / signals
    SPEECH = "speech"
    COMMAND = "command"
    # Fallback
    RAW = "raw"


# ─── SensorReading ───────────────────────────────────────────────────────


class SensorReading(ORBModel):
    """A single reading from one sensor at one moment.

    This is the **lowest-level** perception primitive: raw-ish, tagged with
    its modality and source. Fusion happens later, producing
    :class:`Observation`.
    """

    modality: SensorModality
    source: Annotated[str, Field(min_length=1)]
    """Human-readable sensor identifier (e.g. ``"front_rgb"``, ``"left_force"``)."""
    timestamp: Timestamp
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = 1.0
    payload: dict[str, Any] = Field(default_factory=dict)
    """Modality-specific data. Kept as a dict for forward compatibility."""


# ─── Observation ─────────────────────────────────────────────────────────


class Observation(ORBModel):
    """A structured, fused observation produced by perception.

    Fields
    ------
    observation_id:
        Unique identifier for this observation.
    kind:
        Semantic kind (see :class:`ObservationKind`).
    timestamp:
        When the observation was produced.
    source:
        Identifier of the producer (``"perception"``, ``"simulator"``, …).
    robot_id:
        Optional robot this observation concerns.
    object_id:
        Optional object this observation concerns (e.g. for
        ``OBJECT_DETECTED``).
    agent_id:
        Optional agent this observation concerns.
    pose:
        Optional pose associated with the observation (in world frame).
    confidence:
        Confidence in ``[0, 1]``.
    payload:
        Extensible bag of additional fields.
    readings:
        Optional tuple of raw :class:`SensorReading` that contributed to this
        observation.
    """

    observation_id: ObservationId
    kind: ObservationKind
    timestamp: Timestamp
    source: Annotated[str, Field(min_length=1)] = "perception"
    robot_id: RobotId | None = None
    object_id: ObjectId | None = None
    agent_id: AgentId | None = None
    pose: Pose | None = None
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = 1.0
    payload: dict[str, Any] = Field(default_factory=dict)
    readings: tuple[SensorReading, ...] = ()


__all__ = [
    "Observation",
    "ObservationKind",
    "SensorModality",
    "SensorReading",
    "Vec3",
]
