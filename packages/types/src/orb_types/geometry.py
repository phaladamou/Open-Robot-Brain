"""Geometric primitives for Open Robot Brain.

These are **pure Pydantic** types — serializable, validated, dependency-free.

The choice to avoid NumPy in ``orb_types`` is deliberate: the type layer must
stay lightweight, JSON-friendly, and importable by any downstream consumer
(LLM tools, dashboards, loggers, protocols). NumPy-based conversions belong
in adapters (simulation, control).

Conventions
-----------
- Coordinate system: right-handed, Z-up (world frame).
- Quaternions: ``(w, x, y, z)`` — scalar first, unit norm.
- All positions/orientations are expressed in the **world frame** by default.
  Multi-frame support is handled at the embodiment layer, not here.
"""

from __future__ import annotations

import math
from typing import Annotated

from pydantic import Field, field_validator

from orb_types.base import ORBModel

# ─── Scalars ─────────────────────────────────────────────────────────────

FiniteFloat = Annotated[float, Field(allow_inf_nan=False)]
"""A finite, non-NaN float. Used for all geometric quantities."""


# ─── Vec3 ────────────────────────────────────────────────────────────────


class Vec3(ORBModel):
    """A 3D vector in meters (position, direction, force, …).

    Examples
    --------
    >>> Vec3(x=1.0, y=0.0, z=0.5)
    Vec3(x=1.0, y=0.0, z=0.5)
    """

    x: FiniteFloat = 0.0
    y: FiniteFloat = 0.0
    z: FiniteFloat = 0.0

    @classmethod
    def zero(cls) -> Vec3:
        """Return the zero vector ``(0, 0, 0)``."""
        return cls(x=0.0, y=0.0, z=0.0)

    def to_tuple(self) -> tuple[float, float, float]:
        """Return ``(x, y, z)`` as a plain tuple."""
        return (self.x, self.y, self.z)

    def norm(self) -> float:
        """Return the Euclidean norm."""
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)


# ─── Quaternion ──────────────────────────────────────────────────────────


class Quaternion(ORBModel):
    """A unit quaternion ``(w, x, y, z)`` — scalar first.

    The default value is the identity quaternion ``(1, 0, 0, 0)``.

    Validation
    ----------
    Quaternions must be **non-zero**. They are **not** required to be exactly
    unit norm — callers can normalize via :meth:`normalized`.
    """

    w: FiniteFloat = 1.0
    x: FiniteFloat = 0.0
    y: FiniteFloat = 0.0
    z: FiniteFloat = 0.0

    @field_validator("w", "x", "y", "z")
    @classmethod
    def _check_nonzero(cls, v: float) -> float:
        return v

    def model_post_init(self, __context: object) -> None:
        norm_sq = self.w * self.w + self.x * self.x + self.y * self.y + self.z * self.z
        if norm_sq == 0.0:
            msg = "Quaternion must be non-zero"
            raise ValueError(msg)

    @classmethod
    def identity(cls) -> Quaternion:
        """Return the identity quaternion ``(1, 0, 0, 0)``."""
        return cls(w=1.0, x=0.0, y=0.0, z=0.0)

    def norm(self) -> float:
        """Return the Euclidean norm."""
        return math.sqrt(self.w * self.w + self.x * self.x + self.y * self.y + self.z * self.z)

    def normalized(self) -> Quaternion:
        """Return a unit-norm copy of this quaternion."""
        n = self.norm()
        return Quaternion(w=self.w / n, x=self.x / n, y=self.y / n, z=self.z / n)


# ─── Pose ────────────────────────────────────────────────────────────────


class Pose(ORBModel):
    """A rigid-body pose: position + orientation.

    By convention, poses in ``orb_types`` are expressed in the **world frame**.
    """

    position: Vec3 = Field(default_factory=Vec3.zero)
    orientation: Quaternion = Field(default_factory=Quaternion.identity)

    @classmethod
    def origin(cls) -> Pose:
        """Return the world origin pose."""
        return cls(position=Vec3.zero(), orientation=Quaternion.identity())


# ─── Transform ───────────────────────────────────────────────────────────


class Transform(ORBModel):
    """A named transform between two frames.

    ``parent`` and ``child`` are frame identifiers (e.g. ``"world"``,
    ``"robot_base"``, ``"end_effector"``). The transform maps coordinates
    from ``child`` frame to ``parent`` frame.

    This is a **description** of a transform, not a computation engine.
    Composition of transforms is done at the kinematics layer.
    """

    parent: str
    child: str
    pose: Pose = Field(default_factory=Pose.origin)


__all__ = [
    "FiniteFloat",
    "Pose",
    "Quaternion",
    "Transform",
    "Vec3",
]
