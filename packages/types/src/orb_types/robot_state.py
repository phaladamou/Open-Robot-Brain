"""Robot state representation for Open Robot Brain.

``RobotState`` describes the **body** of a robot at a point in time:
its pose, its joints, and its links. The brain reads this via the
embodiment layer — it never produces it directly.

Design
------
- Immutable snapshot, timestamped.
- Joints and links use tuples (immutability, hashable).
- Units: meters, radians.
- ``RobotState`` is intentionally minimal in v0.1. Fields like force
  sensing, gripper state, battery, and error flags will be added later.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from orb_types.base import ORBModel, Timestamp
from orb_types.geometry import Pose, Vec3
from orb_types.ids import RobotId

# ─── Primitives ──────────────────────────────────────────────────────────

NonEmptyStr = Annotated[str, Field(min_length=1)]


class JointState(ORBModel):
    """State of a single joint.

    ``position`` is in radians for revolute joints, meters for prismatic.
    ``velocity`` is in rad/s or m/s. ``effort`` is in N·m or N.
    """

    name: NonEmptyStr
    position: float = 0.0
    velocity: float = 0.0
    effort: float = 0.0


class LinkState(ORBModel):
    """State of a single rigid link, expressed in world frame."""

    name: NonEmptyStr
    pose: Pose = Field(default_factory=Pose.origin)


# ─── RobotState ──────────────────────────────────────────────────────────


class RobotState(ORBModel):
    """Immutable snapshot of a robot's body state.

    Fields
    ------
    robot_id:
        Which robot this state describes.
    timestamp:
        When this snapshot was produced.
    base_pose:
        World-frame pose of the robot base.
    joints:
        Immutable tuple of joint states (order matches the robot's joint order).
    links:
        Immutable tuple of link states.
    """

    robot_id: RobotId
    timestamp: Timestamp
    base_pose: Pose = Field(default_factory=Pose.origin)
    joints: tuple[JointState, ...] = ()
    links: tuple[LinkState, ...] = ()

    # ─── Lookups ─────────────────────────────────────────────────────────

    def get_joint(self, name: str) -> JointState | None:
        """Return the joint with the given name, or ``None``."""
        for joint in self.joints:
            if joint.name == name:
                return joint
        return None

    def get_link(self, name: str) -> LinkState | None:
        """Return the link with the given name, or ``None``."""
        for link in self.links:
            if link.name == name:
                return link
        return None

    def joint_names(self) -> tuple[str, ...]:
        """Return the tuple of joint names in declared order."""
        return tuple(j.name for j in self.joints)


__all__ = [
    "JointState",
    "LinkState",
    "NonEmptyStr",
    "RobotState",
    "Vec3",
]
