"""Tests for orb_embodiment.adapters.fake."""

from __future__ import annotations

from orb_embodiment import BaseRobot, FakeRobot
from orb_interfaces import CapabilityProvider
from orb_types import CapabilityKind, RobotId, RobotState, utc_now

# ─── Construction ────────────────────────────────────────────────────────


def test_fake_robot_defaults() -> None:
    r = FakeRobot()
    assert r.robot_id == "fake"
    assert r.name == "Fake Robot"


def test_fake_robot_custom_id() -> None:
    r = FakeRobot(robot_id=RobotId("r2d2"), name="R2D2")
    assert r.robot_id == "r2d2"
    assert r.name == "R2D2"


def test_fake_robot_default_capabilities() -> None:
    r = FakeRobot()
    caps = r.capabilities()
    assert caps.has("can_grasp")
    assert caps.has("can_navigate")
    assert caps.has("can_lift")
    assert caps.has("can_see")
    assert caps.has("can_manipulate")


def test_fake_robot_custom_capabilities() -> None:
    r = FakeRobot(capabilities=("can_grasp",))
    caps = r.capabilities()
    assert caps.has("can_grasp")
    assert not caps.has("can_navigate")


def test_fake_robot_empty_capabilities() -> None:
    r = FakeRobot(capabilities=())
    assert r.capabilities().capabilities == ()


# ─── State ───────────────────────────────────────────────────────────────


def test_initial_state_has_robot_id() -> None:
    r = FakeRobot(robot_id=RobotId("r2d2"))
    s = r.initial_state()
    assert s.robot_id == "r2d2"
    assert s.joints == ()


def test_state_returns_current() -> None:
    r = FakeRobot(robot_id=RobotId("r2d2"))
    s = r.state()
    assert s.robot_id == "r2d2"


def test_set_state() -> None:
    r = FakeRobot(robot_id=RobotId("r2d2"))
    new_state = RobotState(robot_id=RobotId("r2d2"), timestamp=utc_now())
    r.set_state(new_state)
    assert r.state() is new_state


# ─── Protocol compliance ─────────────────────────────────────────────────


def test_fake_robot_is_base_robot() -> None:
    r = FakeRobot()
    assert isinstance(r, BaseRobot)


def test_fake_robot_is_capability_provider() -> None:
    r = FakeRobot()
    assert isinstance(r, CapabilityProvider)


# ─── Descriptor ──────────────────────────────────────────────────────────


def test_descriptor_is_consistent_with_robot_id() -> None:
    r = FakeRobot(robot_id=RobotId("arm_01"), name="Arm")
    d = r.descriptor
    assert d.robot_id == "arm_01"
    assert d.name == "Arm"
    assert d.capabilities is r.capabilities()


def test_capability_kinds_are_set() -> None:
    r = FakeRobot()
    caps = r.capabilities()
    grasp = caps.get("can_grasp")
    assert grasp is not None
    assert grasp.kind is CapabilityKind.MANIPULATION


# ─── Extensibility ───────────────────────────────────────────────────────


def test_can_subclass_fake_robot() -> None:
    class MyRobot(FakeRobot):
        pass

    r = MyRobot(robot_id=RobotId("custom"), name="Custom")
    assert r.robot_id == "custom"
    assert isinstance(r, BaseRobot)
