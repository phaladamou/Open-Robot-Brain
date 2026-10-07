"""Tests for orb_types.geometry."""

from __future__ import annotations

import pytest
from orb_types.geometry import Pose, Quaternion, Transform, Vec3
from pydantic import ValidationError as PydanticValidationError

# ─── Vec3 ────────────────────────────────────────────────────────────────


def test_vec3_defaults() -> None:
    v = Vec3()
    assert v.to_tuple() == (0.0, 0.0, 0.0)


def test_vec3_zero() -> None:
    assert Vec3.zero().to_tuple() == (0.0, 0.0, 0.0)


def test_vec3_norm() -> None:
    assert Vec3(x=3.0, y=4.0, z=0.0).norm() == 5.0


def test_vec3_is_frozen() -> None:
    v = Vec3(x=1.0)
    with pytest.raises(PydanticValidationError):
        v.x = 2.0  # type: ignore[misc]


def test_vec3_rejects_nan() -> None:
    with pytest.raises(PydanticValidationError):
        Vec3(x=float("nan"))


def test_vec3_rejects_inf() -> None:
    with pytest.raises(PydanticValidationError):
        Vec3(x=float("inf"))


# ─── Quaternion ──────────────────────────────────────────────────────────


def test_quaternion_identity() -> None:
    q = Quaternion.identity()
    assert (q.w, q.x, q.y, q.z) == (1.0, 0.0, 0.0, 0.0)
    assert q.norm() == 1.0


def test_quaternion_default_is_identity() -> None:
    q = Quaternion()
    assert q.w == 1.0


def test_quaternion_normalized() -> None:
    q = Quaternion(w=2.0, x=0.0, y=0.0, z=0.0)
    n = q.normalized()
    assert n.norm() == pytest.approx(1.0)
    assert n.w == pytest.approx(1.0)


def test_quaternion_rejects_zero() -> None:
    with pytest.raises(PydanticValidationError):
        Quaternion(w=0.0, x=0.0, y=0.0, z=0.0)


# ─── Pose ────────────────────────────────────────────────────────────────


def test_pose_origin() -> None:
    p = Pose.origin()
    assert p.position.to_tuple() == (0.0, 0.0, 0.0)
    assert p.orientation.w == 1.0


def test_pose_custom() -> None:
    p = Pose(position=Vec3(x=1.0, y=2.0, z=3.0))
    assert p.position.x == 1.0


# ─── Transform ───────────────────────────────────────────────────────────


def test_transform() -> None:
    t = Transform(parent="world", child="robot_base")
    assert t.parent == "world"
    assert t.child == "robot_base"
    assert t.pose.position.to_tuple() == (0.0, 0.0, 0.0)


def test_transform_default_pose_is_origin() -> None:
    t = Transform(parent="world", child="robot_base")
    assert t.pose.position.to_tuple() == (0.0, 0.0, 0.0)
    assert t.pose.orientation.w == 1.0
