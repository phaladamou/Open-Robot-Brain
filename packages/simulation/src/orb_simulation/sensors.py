"""Simulated sensors for Open Robot Brain.

A simulator knows the world perfectly — but a brain validated against
perfect information learns nothing about real perception. :class:`MockSensor`
bridges the gap: it reads ground-truth :class:`~orb_types.WorldState` and
produces :class:`~orb_types.Observation` messages shaped like the output of
a real detector (poses with bounded noise, sub-unit confidence), so the
world model, reasoning, and planning layers exercise their real update
paths without any hardware.
"""

from __future__ import annotations

import random

from orb_types import (
    ObjectId,
    Observation,
    ObservationId,
    ObservationKind,
    Pose,
    Vec3,
    WorldState,
    utc_now,
)


class MockSensor:
    """Produce object-detection observations from a world state.

    Each :meth:`sense` call emits one
    :data:`~orb_types.ObservationKind.OBJECT_DETECTED` observation per
    object in the world, in world order. Pose noise is uniform in
    ``[-position_noise, +position_noise]`` per axis, drawn from a private
    seeded generator: two sensors with the same seed produce identical
    streams, and ``position_noise=0.0`` reproduces ground truth exactly.

    Parameters
    ----------
    source:
        Producer identifier stamped on every observation.
    position_noise:
        Half-range of uniform pose noise in meters. Must be ``>= 0``.
    confidence:
        Confidence stamped on every observation. Must be in ``[0, 1]``.
    seed:
        Seed for the private noise generator. ``None`` (default) seeds
        from system entropy; pass an int for reproducible streams.

    Example
    -------
    >>> sensor = MockSensor(position_noise=0.001, seed=7)
    >>> observations = sensor.sense(world)
    """

    def __init__(
        self,
        *,
        source: str = "mock_sensor",
        position_noise: float = 0.0,
        confidence: float = 1.0,
        seed: int | None = None,
    ) -> None:
        if not source:
            msg = "source must be a non-empty string"
            raise ValueError(msg)
        if position_noise < 0.0:
            msg = f"position_noise must be >= 0, got {position_noise!r}"
            raise ValueError(msg)
        if not 0.0 <= confidence <= 1.0:
            msg = f"confidence must be in [0, 1], got {confidence!r}"
            raise ValueError(msg)
        self._source = source
        self._noise = float(position_noise)
        self._confidence = float(confidence)
        self._rng = random.Random(seed)
        self._produced = 0

    def sense(self, world: WorldState) -> tuple[Observation, ...]:
        """Return one detection per object in ``world``.

        Observation IDs are deterministic (``obs_<counter>``): repeated
        runs with the same seed produce identical observations.
        """
        observations: list[Observation] = []
        for obj in world.objects:
            pose = self._noisy_pose(obj.pose)
            observations.append(
                Observation(
                    observation_id=ObservationId(f"obs_{self._produced:06d}"),
                    kind=ObservationKind.OBJECT_DETECTED,
                    timestamp=utc_now(),
                    source=self._source,
                    object_id=ObjectId(obj.object_id),
                    pose=pose,
                    confidence=self._confidence,
                    payload={"type": obj.type, **obj.attributes},
                )
            )
            self._produced += 1
        return tuple(observations)

    def _noisy_pose(self, pose: Pose) -> Pose:
        if self._noise == 0.0:
            return pose
        dx = self._rng.uniform(-self._noise, self._noise)
        dy = self._rng.uniform(-self._noise, self._noise)
        dz = self._rng.uniform(-self._noise, self._noise)
        position = pose.position
        return Pose(
            position=Vec3(x=position.x + dx, y=position.y + dy, z=position.z + dz),
            orientation=pose.orientation,
        )

    # ─── Introspection ──────────────────────────────────────────────────

    @property
    def source(self) -> str:
        """The producer identifier stamped on observations."""
        return self._source

    @property
    def position_noise(self) -> float:
        """Half-range of uniform pose noise in meters."""
        return self._noise

    @property
    def confidence(self) -> float:
        """Confidence stamped on observations."""
        return self._confidence

    @property
    def observations_produced(self) -> int:
        """Total number of observations produced so far."""
        return self._produced


__all__ = ["MockSensor"]
