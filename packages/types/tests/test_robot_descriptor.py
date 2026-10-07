"""Tests for orb_types.robot_descriptor."""

from __future__ import annotations

import pytest
from orb_types import (
    Capability,
    CapabilityId,
    CapabilityKind,
    CapabilitySet,
    RobotDescriptor,
    RobotId,
)
from pydantic import ValidationError as PydanticValidationError


def test_descriptor_minimal() -> None:
    d = RobotDescriptor(robot_id=RobotId("r2d2"), name="R2D2")
    assert d.robot_id == "r2d2"
    assert d.name == "R2D2"
    assert d.capabilities.capabilities == ()
    assert d.urdf_path is None
    assert d.kind is None


def test_descriptor_with_capabilities() -> None:
    caps = CapabilitySet(
        capabilities=(
            Capability(
                capability_id=CapabilityId("can_grasp"),
                name="grasp",
                kind=CapabilityKind.MANIPULATION,
            ),
        )
    )
    d = RobotDescriptor(robot_id=RobotId("arm_01"), name="Arm", capabilities=caps)
    assert d.capabilities.has("can_grasp")


def test_descriptor_rejects_empty_name() -> None:
    with pytest.raises(PydanticValidationError):
        RobotDescriptor(robot_id=RobotId("x"), name="")


def test_descriptor_frozen() -> None:
    d = RobotDescriptor(robot_id=RobotId("x"), name="X")
    with pytest.raises(PydanticValidationError):
        d.name = "Y"  # type: ignore[misc]


def test_descriptor_serializable() -> None:
    d = RobotDescriptor(robot_id=RobotId("x"), name="X", kind="arm")
    payload = d.to_dict()
    assert payload["robot_id"] == "x"
    assert payload["kind"] == "arm"
