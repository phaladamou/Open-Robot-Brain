"""Tests for orb_types.robot_state."""

from __future__ import annotations

import pytest
from orb_types.base import utc_now
from orb_types.geometry import Pose, Vec3
from orb_types.ids import RobotId
from orb_types.robot_state import JointState, LinkState, RobotState
from pydantic import ValidationError as PydanticValidationError

# ─── JointState ──────────────────────────────────────────────────────────


def test_joint_state_defaults() -> None:
    j = JointState(name="joint_1")
    assert j.position == 0.0
    assert j.velocity == 0.0
    assert j.effort == 0.0


def test_joint_state_custom() -> None:
    j = JointState(name="joint_1", position=0.5, velocity=0.1, effort=2.0)
    assert j.position == 0.5


# ─── LinkState ───────────────────────────────────────────────────────────


def test_link_state() -> None:
    link = LinkState(name="link_1", pose=Pose(position=Vec3(x=0.1)))
    assert link.name == "link_1"
    assert link.pose.position.x == 0.1


# ─── RobotState ──────────────────────────────────────────────────────────


def test_robot_state_minimal() -> None:
    rs = RobotState(robot_id=RobotId("r2d2"), timestamp=utc_now())
    assert rs.joints == ()
    assert rs.links == ()
    assert rs.base_pose.position.to_tuple() == (0.0, 0.0, 0.0)


def test_robot_state_with_joints() -> None:
    j1 = JointState(name="joint_1", position=0.1)
    j2 = JointState(name="joint_2", position=0.2)
    rs = RobotState(robot_id=RobotId("r2d2"), timestamp=utc_now(), joints=(j1, j2))
    assert rs.joint_names() == ("joint_1", "joint_2")
    assert rs.get_joint("joint_1") is j1
    assert rs.get_joint("missing") is None


def test_robot_state_get_link() -> None:
    link1 = LinkState(name="link_1")
    rs = RobotState(robot_id=RobotId("r2d2"), timestamp=utc_now(), links=(link1,))
    assert rs.get_link("link_1") is link1
    assert rs.get_link("missing") is None


def test_robot_state_frozen() -> None:
    rs = RobotState(robot_id=RobotId("r2d2"), timestamp=utc_now())
    with pytest.raises(PydanticValidationError):
        rs.robot_id = RobotId("c3po")  # type: ignore[misc]
