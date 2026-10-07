"""Robot descriptor for Open Robot Brain.

A **robot descriptor** is a declarative, serializable description of a
robot: its identity, its human-readable name, and the capabilities it
exposes.

Descriptors are separated from the robot object itself: a descriptor can
be logged, shown in a dashboard, sent over the wire, or stored — without
carrying executable code.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from orb_types.base import ORBModel
from orb_types.capability import CapabilitySet
from orb_types.ids import RobotId


class RobotDescriptor(ORBModel):
    """Declarative description of a robot.

    Fields
    ------
    robot_id:
        Stable identifier (e.g. ``"r2d2"``).
    name:
        Human-readable name.
    capabilities:
        The capability set this robot exposes.
    urdf_path:
        Optional path to a URDF/MJCF/USD file (used by simulators).
    kind:
        Optional coarse kind: ``"arm"``, ``"mobile"``, ``"humanoid"``, …
    """

    robot_id: RobotId
    name: Annotated[str, Field(min_length=1)]
    capabilities: CapabilitySet = Field(default_factory=CapabilitySet)
    urdf_path: str | None = None
    kind: str | None = None


__all__ = ["RobotDescriptor"]
